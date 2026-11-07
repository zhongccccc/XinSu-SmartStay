# -*- coding: utf-8 -*-
"""门锁适配层：mock（今日）/ 串口 / HTTP 三种传输，下午门锁板卡直接切换。

约定协议（ASCII 行协议，便于 MCU 端实现）：
  PC -> 锁控板:  {"cmd":"issue","room":"8801","code":"123456","card":"A1B2C3","ttl":1440}\n
  锁控板 -> PC:  {"ok":true,"msg":"stored"}\n
  PC -> 锁控板:  {"cmd":"open","room":"8801","method":"qr"}\n
"""
import json
import os
import select
import socket
import termios
import threading
import time
import urllib.request

try:
    import tty
except Exception:  # pragma: no cover
    tty = None


class BaseLock:
    transport = "base"

    def issue(self, room, guest, code, card_uid, ttl_min):
        raise NotImplementedError

    def open_door(self, room, method="app"):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError


class MockLock(BaseLock):
    transport = "mock"

    def __init__(self, db=None, log=print):
        self.db = db
        self.log = log
        self.events = []

    def issue(self, room, guest, code, card_uid, ttl_min):
        time.sleep(0.45)  # 模拟串口往返
        evt = {"ts": time.time(), "room": room, "code": code, "card": card_uid,
               "ttl": ttl_min, "guest": guest}
        self.events.append(evt)
        self.log("[lock:mock] issue %s code=%s card=%s" % (room, code, card_uid))
        if self.db:
            self.db.audit("lock_issue", evt)
        return True, "mock-stored"

    def open_door(self, room, method="app"):
        evt = {"ts": time.time(), "room": room, "method": method}
        self.events.append(evt)
        self.log("[lock:mock] open %s via %s" % (room, method))
        if self.db:
            self.db.audit("lock_open", evt)
        return True, "mock-open"

    def status(self):
        return {"transport": self.transport, "online": True, "last": self.events[-1] if self.events else None}


class SerialLock(BaseLock):
    transport = "serial"

    def __init__(self, port="/dev/ttyUSB0", baud=115200, log=print):
        self.port, self.baud, self.log = port, baud, log
        self._fd = None
        self._buf = b""

    def _open(self):
        if self._fd is not None:
            return True
        try:
            fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            attrs = termios.tcgetattr(fd)
            if tty:
                tty.setraw(fd)
            speed_map = {9600: termios.B9600, 115200: termios.B115200,
                         921600: termios.B921600}
            sp = speed_map.get(self.baud, termios.B115200)
            attrs[4] = attrs[5] = sp
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
            self._fd = fd
            return True
        except Exception as e:
            self.log("[lock:serial] open %s failed: %s" % (self.port, e))
            return False

    def _rpc(self, obj, timeout=2.0):
        if not self._open():
            return False, "串口未连接"
        line = (json.dumps(obj, ensure_ascii=False) + "\n").encode()
        try:
            os.write(self._fd, line)
        except Exception as e:
            return False, "写串口失败: %s" % e
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self._fd], [], [], 0.2)
            if r:
                try:
                    self._buf += os.read(self._fd, 512)
                except Exception:
                    break
                if b"\n" in self._buf:
                    resp, self._buf = self._buf.split(b"\n", 1)
                    try:
                        d = json.loads(resp.decode("utf-8", "ignore"))
                        return bool(d.get("ok")), d.get("msg", "")
                    except Exception:
                        return False, "应答解析失败: %r" % resp[:60]
        return False, "锁控板无应答（超时）"

    def issue(self, room, guest, code, card_uid, ttl_min):
        return self._rpc({"cmd": "issue", "room": room, "code": code,
                          "card": card_uid, "ttl": ttl_min, "guest": guest})

    def open_door(self, room, method="app"):
        return self._rpc({"cmd": "open", "room": room, "method": method})

    def status(self):
        ok = self._open()
        return {"transport": self.transport, "online": ok, "port": self.port}


class HttpLock(BaseLock):
    transport = "http"

    def __init__(self, base="http://127.0.0.1:9001", token="", log=print):
        self.base, self.token, self.log = base.rstrip("/"), token, log

    def _rpc(self, path, obj, timeout=3):
        req = urllib.request.Request(self.base + path,
                                     data=json.dumps(obj).encode(),
                                     headers={"Content-Type": "application/json",
                                              "X-Token": self.token})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
                return bool(d.get("ok")), d.get("msg", "")
        except Exception as e:
            return False, "锁控板请求失败: %s" % e

    def issue(self, room, guest, code, card_uid, ttl_min):
        return self._rpc("/issue", {"room": room, "code": code, "card": card_uid, "ttl": ttl_min})

    def open_door(self, room, method="app"):
        return self._rpc("/open", {"room": room, "method": method})

    def status(self):
        try:
            with urllib.request.urlopen(self.base + "/ping", timeout=1.5) as r:
                return {"transport": self.transport, "online": r.status == 200, "url": self.base}
        except Exception:
            return {"transport": self.transport, "online": False, "url": self.base}


class BoardLockAdapter(BaseLock):
    """通晓 RK2206 门锁板（OpenHarmony）。

    auto 模式：板子在线就用板子，离线自动退化为 mock（演示不至于卡住），
    并每 10 秒重试一次，固件刷好后无需重启即可接管。
    """

    transport = "board"

    def __init__(self, port="/dev/ttyUSB1", baud=115200, db=None, log=print,
                 on_event=None, auto=True, fallback=None):
        from .lock_board import BoardLock
        self.port, self.baud, self.db, self.log = port, baud, db, log
        self._user_evt = on_event
        self._auto = auto
        self._use_mock = False
        self._mock = fallback or MockLock(db, log)
        self._board = BoardLock(port, baud, on_event=self._on_evt, log=log)
        ok, detail = self._board.ping(1.2)
        self.log("[lock:board] %s -> %s" % (port, detail))
        if not ok:
            # 串口会随插拔换号：自动扫描所有串口找门锁板
            found = self._scan_ports(baud)
            if found:
                self.port = found
                self._board = BoardLock(found, baud, on_event=self._on_evt, log=log)
                ok, detail = self._board.ping(1.5)
                self.log("[lock:board] 自动发现 %s -> %s" % (found, detail))
        if not ok:
            if auto:
                self._use_mock = True
                self.log("[lock:board] 板子未就绪，暂用 mock（后台每 10s 重试）")
                threading.Thread(target=self._reprobe, daemon=True, name="lock-reprobe").start()
            else:
                self._use_mock = False
        # 看门狗已停用：恢复最初的通讯行为（不周期 ping 板子）
        self._wd_stop = True

    def _watchdog(self):
        """每 15 秒探一次；掉线就重扫端口，回来自动接管。"""
        while not getattr(self, "_wd_stop", False):
            time.sleep(15)
            try:
                if self._use_mock:
                    continue
                ok, _ = self._board.ping(1.0)
                if ok:
                    continue
                self.log("[lock:wd] 板子无应答，重扫端口")
                found = self._scan_ports(self.baud)
                if not found:
                    continue
                from .lock_board import BoardLock
                self.port = found
                self._board = BoardLock(found, self.baud, on_event=self._on_evt, log=self.log)
                ok2, detail = self._board.ping(1.5)
                if ok2:
                    self.log("[lock:wd] 已恢复（%s）%s" % (found, detail))
            except Exception as e:
                self.log("[lock:wd] 异常: %s" % e)

    def _scan_ports(self, baud):
        """遍历所有串口，返回第一个能响应 zk ping 的端口。"""
        import glob
        from .lock_board import BoardLock
        cands = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
        for p in cands:
            if p == self.port:
                continue
            try:
                probe = BoardLock(p, baud, log=lambda *a: None)
                ok, _ = probe.ping(1.0)
                probe.close()
                if ok:
                    self.log("[lock:board] 扫描到门锁板: %s" % p)
                    return p
            except Exception:
                continue
        return None

    def _on_evt(self, t, v):
        try:
            if self.db:
                self.db.audit("lock_event", {"type": t, "value": v})
        except Exception:
            pass
        if self._user_evt:
            try:
                self._user_evt(t, v)
            except Exception:
                pass

    def _reprobe(self):
        while self._use_mock:
            time.sleep(10)
            if not self._use_mock:
                break
            # 不再扫描其它串口（会抢走家居板的数据），只重试自己这个端口
            if self._use_mock and self._board.ping(1.2)[0]:
                self._use_mock = False
                self.log("[lock:board] 门锁板已上线（%s），切换到真实门锁" % self.port)

    def issue(self, room, guest, code, card_uid, ttl_min):
        if self._use_mock:
            # 板子没连上：直接报错，绝不能让界面以为下发成功
            return False, "门锁板未连接（请检查门锁板供电/USB）"

        ok, detail = self._board.issue(room, guest, code, card_uid, ttl_min)
        if ok and self.db:
            self.db.audit("lock_issue", {"room": room, "code": code,
                                         "card": card_uid, "ttl": ttl_min,
                                         "via": "board"})
        return ok, detail

    def open_door(self, room, method="app"):
        if self._use_mock:
            return self._mock.open_door(room, method)
        ok, detail = self._board.open_door(room, method)
        if ok and self.db:
            self.db.audit("lock_open", {"room": room, "method": method, "via": "board"})
        return ok, detail

    def revoke(self, room="all"):
        """退房时作废板子上的凭证。"""
        if self._use_mock:
            return True, "mock-revoked"
        ok, detail = self._board.revoke(room)
        if ok and self.db:
            self.db.audit("lock_revoke", {"room": room, "via": "board"})
        return ok, detail

    def validate_code(self, pin):
        """门锁板本地校验开门码。mock 模式下用内存凭证比对。"""
        if self._use_mock:
            hit = any(True for _ in [0]) and str(pin) == str(self._mock_pin or "")
            return hit, "mock-verify"
        ok, detail = self._board.validate_code(pin)
        self.db.audit("lock_verify", {"pin_len": len(str(pin)), "ok": ok, "via": "board"})
        return ok, detail

    def status(self):
        st = dict(self._board.status())
        st["mock"] = self._use_mock
        st["port"] = self.port
        return st


def build_lock(cfg, db, log=print, on_event=None):
    conf = cfg.get("lock", {})
    t = conf.get("transport", "mock")
    if t in ("board", "auto"):
        return BoardLockAdapter(conf.get("port", "/dev/ttyUSB1"),
                                int(conf.get("baud", 115200)),
                                db, log, on_event=on_event,
                                auto=(t == "auto"))
    if t == "serial":
        return SerialLock(conf.get("serial", "/dev/ttyUSB0"), conf.get("baud", 115200), log)
    if t == "http":
        return HttpLock(conf.get("http", "http://127.0.0.1:9001"), conf.get("token", ""), log)
    return MockLock(db, log)
