# -*- coding: utf-8 -*-
"""智能门锁板（通晓 RK2206 / OpenHarmony 轻量系统）串口驱动。

板子在日志串口上跑着 OHOS shell，我们的应用把协议注册成了 **shell 子命令**：

    K1 发送（以 \\r 结束）：  zk ping
                             zk issue <room> <code> <card|-> <ttl_min>
                             zk open <room>
                             zk revoke <room>

    板子回打印（行首 ZK|）：  ZK|ACK|ISSUE|OK|room=8801
                             ZK|EVT|DOOR|open   等

这样做的好处：不需要和 shell 抢同一个 UART 的输入，字节不会被吞；
控制台的提示符/回显一律被忽略，只认行内出现的 `ZK|` 片段。
"""
import os
import select
import termios
import threading
import time

SPEEDS = {9600: termios.B9600, 19200: termios.B19200, 38400: termios.B38400,
          57600: termios.B57600, 115200: termios.B115200}
MARK = "ZK|"


class BoardLock:
    transport = "board"

    def __init__(self, port="/dev/ttyUSB1", baud=115200, on_event=None, log=print):
        self.port = port
        self.baud = baud
        self.on_event = on_event
        self.log = log
        self.online = False
        self.firmware = None
        self._fd = None
        self._buf = b""
        self._lock = threading.Lock()
        self._ack = {}
        self._evt = threading.Event()
        self._stop = False
        self._reader = None
        self.last_event = None

    # ---------- 串口 ----------
    def open(self):
        try:
            fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except OSError as e:
            self.log("[lock] 打开 %s 失败: %s" % (self.port, e))
            return False
        a = termios.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
        a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = SPEEDS.get(self.baud, termios.B115200)
        a[6][termios.VMIN] = 0
        a[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, a)
        self._fd = fd
        self._start_reader()
        return True

    def close(self):
        self._stop = True
        try:
            if self._fd is not None:
                os.close(self._fd)
        except Exception:
            pass
        self._fd = None
        self.online = False

    @property
    def is_open(self):
        return self._fd is not None

    # ---------- 收 ----------
    def _start_reader(self):
        if self._reader and self._reader.is_alive():
            return
        self._stop = False
        self._reader = threading.Thread(target=self._loop, daemon=True, name="lock-board")
        self._reader.start()

    def _loop(self):
        while not self._stop and self._fd is not None:
            try:
                r, _, _ = select.select([self._fd], [], [], 0.3)
            except (OSError, ValueError):
                break
            if not r:
                continue
            try:
                data = os.read(self._fd, 4096)
            except (BlockingIOError, OSError):
                continue
            if not data:
                continue
            self._buf += data
            while b"\n" in self._buf:
                line, self._buf = self._buf.split(b"\n", 1)
                self._handle(line.decode("utf-8", "ignore").strip())

    def _handle(self, line):
        if MARK not in line:
            return                      # 控制台噪声 / 回显
        payload = line[line.index(MARK) + len(MARK):]
        parts = payload.split("|")
        if not parts:
            return
        kind = parts[0].upper()
        if kind == "PONG":
            self.online = True
        elif kind == "ACK" and len(parts) >= 3:
            cmd, status = parts[1].upper(), parts[2].upper()
            detail = "|".join(parts[3:])
            self._ack[cmd] = (status == "OK", detail)
            self._evt.set()
        elif kind == "EVT" and len(parts) >= 2:
            evt = parts[1].upper()
            value = "|".join(parts[2:])
            self.last_event = {"type": evt, "value": value, "ts": time.time()}
            self.log("[lock] 事件 %s: %s" % (evt, value))
            if self.on_event:
                try:
                    self.on_event(evt, value)
                except Exception as e:
                    self.log("[lock] on_event 异常: %s" % e)

    # ---------- 发 ----------
    def _send(self, args):
        if self._fd is None:
            return False
        try:
            os.write(self._fd, ("zk " + args + "\r").encode())
            return True
        except OSError as e:
            self.log("[lock] 写串口失败: %s" % e)
            self.close()
            return False

    def _wait_ack(self, cmd, timeout):
        end = time.time() + timeout
        while time.time() < end:
            if cmd in self._ack:
                return self._ack.pop(cmd)
            self._evt.wait(0.15)
        return False, "板子无应答（超时）"

    def _call(self, args, ack, timeout):
        """先清旧应答再发送，避免把刚到的 ACK 误清掉。"""
        self._ack.pop(ack, None)
        self._evt.clear()
        if not self._send(args):
            return False, "串口未打开"
        return self._wait_ack(ack, timeout)

    # ---------- 对上层接口 ----------
    def ping(self, timeout=2.5):
        if not self.is_open and not self.open():
            return False, "串口打不开"
        ok, detail = self._call("ping", "PING", timeout)
        if ok:
            self.online = True
            self.firmware = detail or None
            return True, detail or "pong"
        return self.online, detail

    def issue(self, room, guest, code, card_uid, ttl_min):
        if not self.is_open and not self.open():
            return False, "门锁板串口打不开"
        ok, detail = self._call("issue %s %s %s %d" % (room, code, card_uid or "-", ttl_min),
                                "ISSUE", 4.0)
        if ok:
            self.online = True
        return ok, detail or ("已写入门锁" if ok else "失败")

    def open_door(self, room, method="kiosk"):
        if not self.is_open and not self.open():
            return False, "门锁板串口打不开"
        ok, detail = self._call("open %s" % room, "OPEN", 4.0)
        return ok, detail or ("开门指令已下发" if ok else "失败")

    def validate_code(self, pin):
        """把开门码交给板子**本地**校验（安全性在门锁端）。"""
        if not self.is_open and not self.open():
            return False, "门锁板串口打不开"
        self._code_result = None
        ok, detail = self._call("code %s" % pin, "CODE", 4.0)
        return ok, detail or ("校验通过" if ok else "校验失败")

    def revoke(self, room="all"):
        if not self.is_open and not self.open():
            return False, "门锁板串口打不开"
        # room 为空或 "all" 时清空全部；否则只作废该房间（固件 v58 支持）
        if not room or str(room).lower() == "all":
            cmd = "revoke"
        else:
            cmd = "revoke %s" % room
        ok, detail = self._call(cmd, "REVOKE", 3.0)
        return ok, detail or ("凭证已作废" if ok else "失败")

    def status(self):
        return {"transport": "board", "port": self.port, "online": self.online,
                "firmware": self.firmware, "last_event": self.last_event}


if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB1"
    lk = BoardLock(port, on_event=lambda t, v: print("EVENT", t, v))
    print("ping:", lk.ping())
    print("issue:", lk.issue("8801", "测试", "123456", "-", 60))
    time.sleep(1)
    print("status:", lk.status())
