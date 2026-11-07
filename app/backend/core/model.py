# -*- coding: utf-8 -*-
"""入住状态机：待机 → 身份证 → 人脸 → 选房 → 支付 → 发卡 → 下发门锁 → 完成。"""
import random
import threading
import time

from ..config import CONF
from .bus import BUS

STEPS = ["idle", "ident", "face", "room", "pay", "card", "issue", "done"]
STEP_LABEL = {
    "idle": "待机", "ident": "身份核验", "face": "人脸采集", "room": "选择房间",
    "pay": "支付", "card": "发放房卡", "issue": "下发门锁", "done": "完成",
}

MOCK_GUESTS = [
    ("陈思远", "4403**********2418"),
    ("李梦琪", "4403**********0627"),
    ("王浩然", "4401**********5513"),
    ("赵一诺", "4403**********8842"),
]


class Controller:
    """单台一体机的业务状态机（单客人串行）。"""

    def __init__(self, db, devices, audio, lock):
        self.db = db
        self.devices = devices
        self.audio = audio
        self.lock = lock
        self._last_room = None
        self.last_card = None
        self._lk = threading.RLock()
        self._idle_timer = None
        self.state = {
            "step": "idle",
            "step_label": STEP_LABEL["idle"],
            "guest": None,
            "idno": None,
            "face": None,
            "room": None,
            "price": 0,
            "card_uid": None,
            "order_id": None,
            "lock_code": None,
            "msg": "",
            "started_at": None,
            "updated": time.time(),
        }

    # ---------- 基础 ----------
    def snapshot(self):
        with self._lk:
            s = dict(self.state)
        s["inhouse"] = self.db.inhouse_orders()
        s["workorders"] = self.db.workorders(8)
        # 房间列表附带"是否已订"，供界面置灰
        try:
            busy = {o["room"] for o in self.db.inhouse_orders()}
        except Exception:
            busy = set()
        rooms = []
        for r in CONF["rooms"]:
            rr = dict(r)
            rr["occupied"] = r["no"] in busy
            rooms.append(rr)
        s["rooms"] = rooms
        s["hotel"] = CONF["hotel"]
        s["hotel_sub"] = CONF["hotel"]["sub"]
        try:
            s["camera_ok"] = bool(self.devices.camera.info().get("ok"))
        except Exception:
            s["camera_ok"] = False
        return s

    def _publish(self):
        BUS.publish("state", self.snapshot())

    def _goto(self, step, msg="", **kw):
        with self._lk:
            self.state.update(kw)
            self.state["step"] = step
            self.state["step_label"] = STEP_LABEL.get(step, step)
            self.state["msg"] = msg
            self.state["updated"] = time.time()
        self._publish()
        return self.snapshot()

    def _say(self, text):
        if text:
            self.audio.say(text)

    # ---------- 房间环境（智能家居板） ----------
    home = None

    def attach_home(self, board):
        self.home = board

    def apply_room_mode(self, mode, room=None):
        """把房间切到某个模式：welcome(迎宾) / eco(节能) / bright(明亮)。

        这是**入住流程驱动房间状态**，不是前台远程遥控：
        客人办完入住，房间自动亮灯通风；退房后自动断掉，省电。
        """
        if not self.home:
            return False
        try:
            ok = self.home.apply_mode(mode)
            self.db.audit("room_mode", {"mode": mode, "room": room, "ok": bool(ok)})
            return bool(ok)
        except Exception as e:
            self.db.audit("error", {"where": "room_mode", "err": str(e)})
            return False

    def _arm_idle(self):
        """完成后 N 秒自动回待机。"""
        if self._idle_timer:
            self._idle_timer.cancel()

        def reset():
            with self._lk:
                if self.state["step"] == "done":
                    self._goto("idle", "欢迎光临，请触摸屏幕开始入住")

        self._idle_timer = threading.Timer(CONF["kiosk"].get("idle_timeout", 60), reset)
        self._idle_timer.daemon = True
        self._idle_timer.start()

    # ---------- 流程动作 ----------
    def start(self):
        with self._lk:
            if self.state["step"] not in ("idle", "done"):
                return self.snapshot()
            self.state.update({"guest": None, "idno": None, "face": None, "room": None,
                               "price": 0, "card_uid": None, "order_id": None,
                               "lock_code": None, "started_at": time.time()})
        self._say("欢迎入住芯宿智控智慧酒店，请将身份证放在读卡区")
        return self._goto("ident", "芯片面朝上，平放于感应区，保持 6 秒")

    def on_idcard(self, name, idno, extra=None):
        with self._lk:
            if self.state["step"] != "ident":
                return self.snapshot()
        if extra and extra.get("photo_path"):
            self.id_photo_path = extra["photo_path"]
        self.db.audit("idcard", {"name": name, "idno": idno,
                                 "has_photo": bool(extra and extra.get("photo_path"))})
        self._say("身份核验通过，请正对摄像头，为您采集人脸")
        return self._goto("face", "核验通过：%s，请正对摄像头" % name, guest=name, idno=idno)

    def mock_idcard(self):
        name, idno = random.choice(MOCK_GUESTS)
        return self.on_idcard(name, idno, {"mock": True})

    def on_face(self, photo_path=None, score=0.93, passed=True, reason=""):
        with self._lk:
            if self.state["step"] != "face":
                return self.snapshot()
        self.db.audit("face", {"photo": photo_path, "score": score,
                               "passed": bool(passed), "reason": reason})
        if not passed:
            msg = reason or "未通过比对，请正对摄像头再试一次"
            self._say("人脸比对未通过，请正对摄像头再试一次")
            with self._lk:
                self.state["msg"] = msg
                self.state["face_score"] = score
                self.state["face_reason"] = msg
            return self.snapshot()
        self._say("人脸比对成功，请选择您喜欢的房间")
        return self._goto("room", "比对成功，请选择房间", face=photo_path or "snapshot",
                          face_score=score)

    def choose_room(self, room_no):
        with self._lk:
            if self.state["step"] != "room":
                return self.snapshot()
        room = next((r for r in CONF["rooms"] if r["no"] == str(room_no)), None)
        if not room:
            return self.snapshot()
        self._say("已选择房间，请扫描付款码支付")
        return self._goto("pay", "请扫描付款码支付 ¥%d" % room["price"],
                          room=room, price=room["price"])

    def on_paycode(self, code):
        """二维码识别器读到付款码。"""
        with self._lk:
            if self.state["step"] != "pay":
                return self.snapshot()
            room = self.state["room"]
        self.db.audit("pay", {"code": code[:4] + "****", "amount": room["price"]})
        self._say("支付成功，请将房卡放在读卡区为您写卡")
        snap = self._goto("card", "支付成功，请将房卡放在读卡区", card_uid=None)
        threading.Thread(target=self._card_skip_after, args=(45,),
                         daemon=True, name="card-timeout").start()
        return snap

    def _card_skip_after(self, seconds):
        """房卡步骤超时自动放行（读卡器无响应时不阻塞入住）。"""
        time.sleep(seconds)
        with self._lk:
            if self.state["step"] != "card":
                return
        self.on_card("-")

    def on_card(self, uid):
        """RFID 读卡器读到房卡 UID。

        - 处在「房卡」步骤：绑定房卡并下发门锁权限
        - 其它时候：当作「房卡开门」——用最先接的 USB 读卡器刷在住房卡开门
        """
        with self._lk:
            if self.state["step"] != "card":
                return self._card_unlock(uid)
        self._say("房卡写入成功，正在为您下发门锁权限")
        snap = self._goto("issue", "房卡写入成功：%s" % uid, card_uid=uid)
        # 关键：界面只负责显示，真正的下发由后端自己触发，
        # 否则前端停在"正在下发门锁凭证"不会有任何进展
        threading.Thread(target=self._auto_issue, daemon=True, name="auto-issue").start()
        return snap

    def _card_unlock(self, uid):
        """大堂一体机刷房卡：

        - 卡号匹配到在住订单 → **办退房**（作废门锁凭证 + 关单）
        - 匹配不到 → 提示未找到入住记录
        """
        uid = (uid or "").strip().upper()
        order = None
        for o in self.db.inhouse_orders():
            if (o["card_uid"] or "").strip().upper() == uid:
                order = o
                break

        if not order:
            self.last_card = {"ok": False, "mode": "checkout", "uid": uid,
                              "room": None, "reason": "no-order"}
            self.db.audit("checkout_denied", dict(self.last_card))
            self._say("没有找到这张卡的入住记录，请到前台办理退房")
            return self.snapshot()

        room = order["room"]
        ok, detail = False, ""
        try:
            ok, detail = self.lock.revoke(room)
        except Exception as e:
            detail = str(e)
        try:
            self.db.checkout(order["id"])
        except Exception as e:
            self.db.audit("error", {"where": "checkout", "err": str(e)})

        self.last_card = {"ok": ok, "mode": "checkout", "uid": uid,
                          "room": room, "reason": str(detail)[:40]}
        self.db.audit("lock_checkout", dict(self.last_card))
        self._say("退房成功，开门凭证已作废")
        return self.snapshot()

    def _auto_issue(self):
        time.sleep(0.4)          # 让界面把"下发中"画出来
        for attempt in range(1, 4):
            try:
                self.issue()
                if self.state["step"] == "done":
                    return
            except Exception as e:
                self.db.audit("error", {"where": "auto_issue", "err": str(e), "try": attempt})
            if self.state["step"] != "issue":
                return
            time.sleep(1.5)
        # 三次都没成：不再卡死，带着已生成的开门码进入完成页并标注
        with self._lk:
            code = self.state.get("lock_code")
            room = self.state.get("room")
        if self.state["step"] == "issue" and code:
            self._goto("done", "门锁未响应，凭证已生成（可人工门锁核验）", lock_code=code)
            self._arm_idle()
            self._say("门锁未响应，开门码已生成，请到前台处理")

    def issue(self):
        """生成临时开门码并下发给门锁（可重复调用，已完成的会忽略）。"""
        with self._lk:
            # 只允许在 issue 步骤执行；用户中途「返回」后，后台线程不会误发
            if self.state["step"] != "issue":
                return self.snapshot()
            st = dict(self.state)
        # 门锁板键盘的 "2" 键存在帧对齐缺陷（读数与 0 撞位），
        # 为确保演示可用，开门码只使用 0,1,3-9，不含 2
        _d = "013456789"
        code = "".join(random.choice(_d) for _ in range(6))
        self._last_room = st["room"]["no"]   # 退房时用来作废凭证
        ok, detail = self.lock.issue(st["room"]["no"], st["guest"], code, st["card_uid"], 24 * 60)
        oid = self.db.create_order(st["guest"], st["idno"], st["room"]["no"], st["price"],
                                   st["card_uid"], code, {"lock": detail})
        if ok:
            self._say("开门码已生成，祝您入住愉快")
            self._goto("done", "开锁凭证已下发，祝您入住愉快", lock_code=code, order_id=oid)
            self._arm_idle()
            pass
        else:
            self._goto("issue", "门锁下发失败：%s" % detail, lock_code=code)
        return self.snapshot()

    def cancel(self):
        # 退房/复位时把门锁板上的凭证作废（凭板子状态决定成败，不阻塞流程）
        room = (self.state.get("room") or {}).get("no") or getattr(self, "_last_room", None)
        if room and hasattr(self.lock, "revoke"):
            try:
                ok, detail = self.lock.revoke(room)
                self.db.audit("lock_revoke", {"room": room, "ok": ok, "detail": str(detail)[:60]})
            except Exception as e:
                self.db.audit("error", {"where": "revoke", "err": str(e)})
        self._say("已取消，欢迎再次使用")
        return self._goto("idle", "欢迎光临，请触摸屏幕开始入住",
                          guest=None, idno=None, room=None, price=0, card_uid=None,
                          order_id=None, lock_code=None, face=None)

    def find_order_by_code(self, pin):
        """按开门码找到对应的在住订单。"""
        pin = str(pin or "").strip()
        if not pin:
            return None
        for o in self.db.inhouse_orders():
            code = (o["lock_code"] or "").strip()
            if code and code == pin:
                return o
        return None

    def checkout_guide(self):
        """客人点「我要退房」时调用：播报怎么退房，不改流程状态。"""
        self._say("请将房卡放在读卡区办理退房，没有房卡可以输入开门码")
        return self.snapshot()

    def checkout_by_code(self, pin):
        """凭开门码退房：码对得上才退，否则拒绝。"""
        order = self.find_order_by_code(pin)
        if not order:
            self.db.audit("checkout_code_denied", {"pin_len": len(str(pin or ""))})
            self._say("开门码不正确，请核对后重试")
            return {"ok": False, "reason": "code-mismatch",
                    "msg": "开门码不正确，请核对后重试，或联系前台"}
        snap = self.checkout(order["room"])
        snap["checked_out_room"] = order["room"]
        return {"ok": True, "room": order["room"], "msg": "退房成功", "state": snap}

    def checkout(self, room=None):
        """退房：作废门锁板上的凭证，关单，再回待机。

        room 为空时退回"本单房间"→"最近下发房间"。
        """
        room = room or (self.state.get("room") or {}).get("no") \
            or getattr(self, "_last_room", None)
        ok = False
        detail = ""
        if room and hasattr(self.lock, "revoke"):
            try:
                ok, detail = self.lock.revoke(room)
                self.db.audit("lock_checkout", {"room": room, "ok": ok,
                                                "detail": str(detail)[:60]})
            except Exception as e:
                self.db.audit("error", {"where": "checkout", "err": str(e)})
        # 关掉该房间的在住订单
        try:
            for o in self.db.inhouse_orders():
                if o["room"] == room:
                    self.db.checkout(o["id"])
                    break
        except Exception as e:
            self.db.audit("error", {"where": "order_checkout", "err": str(e)})
        self._say("退房成功，开门凭证已作废")
        return self._goto("idle", "退房完成，凭证已作废｜欢迎再次光临",
                          guest=None, idno=None, room=None, price=0, card_uid=None,
                          order_id=None, lock_code=None, face=None)

    def reset(self):
        """仅回待机，保留门锁凭证（"完成并返回"用）。"""
        with self._lk:
            room_no = (self.state.get("room") or {}).get("no")
            code = self.state.get("lock_code")
        if room_no and code:
            digits = "，".join(str(code))
            self._say("办理完成，请取走身份证和房卡，到房间输入开门码即可开锁")
        else:
            self._say("办理完成，请取走身份证和房卡，到房间输入开门码即可开锁")
        return self._goto("idle", "办理完成｜请到房间用开门码或指纹开锁",
                          guest=None, idno=None, room=None, price=0, card_uid=None,
                          order_id=None, lock_code=None, face=None)

    # ---------- 返回（界面上的 ‹ 按钮）----------
    BACK_MAP = {
        "ident": "idle",
        "face": "ident",
        "room": "face",
        "pay": "room",
        "card": "pay",
        "issue": "card",
        "done": "idle",
    }

    def back(self):
        """回退一步，并清掉被放弃步骤已填的数据。"""
        with self._lk:
            step = self.state["step"]
        target = self.BACK_MAP.get(step)
        if not target:
            return self.snapshot()

        empty = dict(guest=None, idno=None, face=None, room=None, price=0,
                     card_uid=None, lock_code=None, order_id=None)
        if target == "idle":
            kw, msg = empty, "欢迎光临，请触摸屏幕开始入住"
        elif target == "ident":
            kw, msg = empty, "芯片面朝上，平放于感应区，保持 6 秒"
        elif target == "face":
            kw = dict(room=None, price=0, card_uid=None, lock_code=None, order_id=None)
            msg = "请正对摄像头"
        elif target == "room":
            kw = dict(room=None, price=0, card_uid=None)
            msg = "请选择房间"
        elif target == "pay":
            kw = dict(card_uid=None)
            msg = "请扫描付款码支付"
        else:  # card
            kw = dict(card_uid=None)
            msg = "请将房卡放在读卡区"

        self.db.audit("back", {"from": step, "to": target})
        if target == "idle":
            self._say("已返回待机")
        return self._goto(target, msg, **kw)

    # ---------- 语音 / 服务 ----------
    def voice(self, text, room=None):
        text = (text or "").strip()
        if not text:
            return {"reply": "", "action": None}
        room = room or (self.state.get("room") or {}).get("no") or "8801"
        kind, action = self._route(text)
        if kind in ("灯光", "空调", "窗帘"):
            reply = "好的，已为您%s" % action
            self.db.create_workorder(room, "[设备联动] " + action, "control")
        elif kind == "服务":
            wid = self.db.create_workorder(room, action, "service")
            reply = "已为您呼叫服务：%s，工单号 %d，预计 8 分钟送达" % (action, wid)
        elif kind == "查询":
            reply = self._query(action)
        else:
            reply = "抱歉，我还没有学会这个指令，您可以试试：送拖鞋、开灯、退房时间"
            action = "unknown"
        self._say(reply)
        self.db.audit("voice", {"text": text, "reply": reply})
        # 带唯一 id：HTTP 返回和 SSE 推送是同一条消息，前端按 id 去重，
        # 否则同一次对话会被渲染两遍（用户气泡和回复气泡各两份）
        mid = "%d-%d" % (int(time.time() * 1000), random.randint(100, 999))
        BUS.publish("voice", {"id": mid, "text": text, "reply": reply, "room": room})
        return {"id": mid, "reply": reply, "action": action, "kind": kind, "room": room}

    def _route(self, text):
        from ..config import VOICE_COMMANDS
        for kind, words in VOICE_COMMANDS.items():
            for w in words:
                if w in text:
                    return kind, self._action_text(kind, text)
        return "未知", None

    def _action_text(self, kind, text):
        if kind == "灯光":
            if "关" in text:
                return "关闭全部灯光"
            if "睡眠" in text:
                return "切换睡眠模式（关主灯/开夜灯）"
            return "打开灯光"
        if kind == "空调":
            if "关" in text:
                return "关闭空调"
            return "空调调至 26 度"
        if kind == "窗帘":
            return "关闭窗帘" if "关" in text else "打开窗帘"
        if kind == "服务":
            for w in ("拖鞋", "牙刷", "毛巾", "矿泉水", "打扫", "被子", "枕头"):
                if w in text:
                    return "配送" + w
            return "客房服务"
        return text

    def _query(self, text):
        if "退房" in text:
            return "本店退房时间为次日 12:00，支持一键退房，无需到前台"
        if "早餐" in text:
            return "早餐时间为 07:00-10:00，位于 3 层全日制餐厅"
        if "wifi" in text.lower():
            return "无线网络名称 XINSU-GUEST，密码 88888888"
        if "停车" in text:
            return "住店客人可免费停车，凭房卡至 B1 前台登记"
        return "已为您查询"
