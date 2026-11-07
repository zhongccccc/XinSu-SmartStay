# -*- coding: utf-8 -*-
"""入住→房间迎宾模式；退房→房间节能复位。"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

# 1) Controller 持有一个家居板引用 + 应用模式
if "def attach_home" not in s:
    anchor = "    def _arm_idle(self):"
    helper = '''    # ---------- 房间环境（智能家居板） ----------
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

'''
    s = s.replace(anchor, helper + anchor, 1)
    print("model.py: 房间模式已加")

# 2) 入住成功 → 迎宾模式
s = s.replace('''            self._goto("done", "开锁凭证已下发，祝您入住愉快", lock_code=code, order_id=oid)
            self._arm_idle()''',
'''            self._goto("done", "开锁凭证已下发，祝您入住愉快", lock_code=code, order_id=oid)
            self._arm_idle()
            threading.Thread(target=self.apply_room_mode, args=("welcome", st["room"]["no"]),
                             daemon=True, name="room-welcome").start()''', 1)

# 3) 退房 → 节能复位
s = s.replace('''            # 关掉该房间的在住订单''',
'''            # 房间节能复位（灯/风扇全关）
            self.apply_room_mode("eco", room)
            # 关掉该房间的在住订单''', 1)

open(P, "w", encoding="utf-8").write(s)
print("model.py: 入住/退房联动已加")

# 4) HomeBoard.apply_mode
H = r"E:\zhikong\app\backend\devices\home_board.py"
h = open(H, encoding="utf-8").read()
if "def apply_mode" not in h:
    h = h.replace("    def beep(self, ms=150):",
'''    def apply_mode(self, mode):
        """房间模式：welcome 亮灯+低风 / eco 全关 / bright 亮灯+强风。"""
        mode = (mode or "").lower()
        if mode == "welcome":
            a = self.light(True)
            b = self.fan(30)
            return a or b
        if mode == "bright":
            self.light(True)
            return self.fan(60)
        # 默认 eco
        self.light(False)
        self.fan(0)
        return True

    def beep(self, ms=150):''', 1)
    open(H, "w", encoding="utf-8").write(h)
    print("home_board.py: apply_mode 已加")

# 5) main.py 绑定
M = r"E:\zhikong\app\backend\main.py"
m = open(M, encoding="utf-8").read()
if "attach_home" not in m:
    m = m.replace("        self._home_alarm_at = 0.0",
                  "        self._home_alarm_at = 0.0\n        self.ctrl.attach_home(self.home)", 1)
    open(M, "w", encoding="utf-8").write(m)
    print("main.py: 已绑定家居板到控制器")
