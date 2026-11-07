# -*- coding: utf-8 -*-
"""RFID V23B 串口读卡器（CH340）。

协议（来自厂商 C++ 样例与使用手册）：
  发送  01 08 A1 20 00 01 00 76                 读卡号
  成功  TT 0C CC 20 00 <2B 卡类型> <4B 卡号> <CK>
  失败  TT 08 CC 20 01 00 00 <CK>
  校验  CK = ~XOR(前面所有字节)
  串口  9600 8N1，读写器地址 0x20
注意：实测应答帧前面可能带若干 0x00 填充，因此按「长度字节 + 校验和」扫帧，不写死包类型。
"""
import os
import select
import termios
import threading
import time

CMD_READ_ID = bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])
SPEEDS = {4800: termios.B4800, 9600: termios.B9600, 19200: termios.B19200,
          38400: termios.B38400, 57600: termios.B57600, 115200: termios.B115200}


def _checksum_ok(buf):
    c = 0
    for b in buf[:-1]:
        c ^= b
    return buf[-1] == (~c) & 0xFF


def scan_frames(buf):
    out = []
    i = 0
    while i + 4 <= len(buf):
        n = buf[i + 1]
        if 4 <= n <= 32 and i + n <= len(buf):
            cand = buf[i:i + n]
            if _checksum_ok(cand):
                out.append(cand)
                i += n
                continue
        i += 1
    return out


class SerialRfid:
    def __init__(self, on_card, port="/dev/ttyUSB0", baud=9600,
                 debounce=3.0, log=print):
        self.on_card = on_card
        self.port = port
        self.baud = baud
        self.debounce = debounce
        self.log = log
        self.online = False
        self.last_uid = None
        self.last_ts = 0
        self.reads = 0
        self._idle = 0
        self._last_frame_ts = time.time()
        self._stop = False
        self._fd = None

    # ---------- 串口 ----------
    def _find_port(self):
        return None   # 已停用：不再扫描其它串口

        """遍历串口，发一次读卡命令，谁回包用谁。"""
        import glob as _glob
        for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):
            if p == self.port:
                continue
            try:
                fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            except OSError:
                continue
            try:
                a = termios.tcgetattr(fd)
                a[0] = a[1] = 0
                a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
                a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
                a[3] = 0
                a[4] = a[5] = SPEEDS.get(self.baud, termios.B9600)
                a[6][termios.VMIN] = 0
                a[6][termios.VTIME] = 0
                termios.tcsetattr(fd, termios.TCSANOW, a)
                try:
                    while os.read(fd, 1024):
                        pass
                except BlockingIOError:
                    pass
                os.write(fd, CMD_READ_ID)
                buf = b""
                end = time.time() + 0.4
                while time.time() < end:
                    r, _, _ = select.select([fd], [], [], 0.05)
                    if r:
                        try:
                            buf += os.read(fd, 256)
                        except (BlockingIOError, OSError):
                            break
                frames = scan_frames(buf) if buf else []
                if frames and any(len(f) >= 12 for f in frames):
                    self.log("[rfid] 在 %s 发现读卡器" % p)
                    self.port = p
                    return p
            except Exception:
                pass
            finally:
                try:
                    os.close(fd)
                except OSError:
                    pass
        return None

    def _open(self):
        try:
            fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except OSError as e:
            now = time.time()
            if now - getattr(self, "_last_err_log", 0) > 30:
                self._last_err_log = now
                self.log("[rfid] open %s failed: %s" % (self.port, e))
            self.online = False
            return None
        self._last_err_log = 0
        a = termios.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
        a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = SPEEDS.get(self.baud, termios.B9600)
        a[6][termios.VMIN] = 0
        a[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, a)
        self._fd = fd
        self.online = True
        return fd

    def _close(self):
        try:
            if self._fd is not None:
                os.close(self._fd)
        except Exception:
            pass
        self._fd = None
        self.online = False

    def _transact(self, timeout=0.45):
        fd = self._fd
        try:
            os.write(fd, CMD_READ_ID)
        except OSError:
            self._close()
            return []
        buf = b""
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                try:
                    buf += os.read(fd, 512)
                except (BlockingIOError, OSError):
                    break
        return scan_frames(buf)

    # ---------- 主循环 ----------
    def start(self):
        threading.Thread(target=self._loop, daemon=True, name="rfid").start()

    def _loop(self):
        while not self._stop:
            if self._fd is None:
                if self._open() is None:
                    time.sleep(2)
                    continue
                time.sleep(0.2)
                try:
                    os.read(self._fd, 1024)      # 丢掉上电噪声
                except Exception:
                    pass
            frames = self._transact()
            # 注意：这里绝不能去扫描/打开其它串口（会抢走门锁板/家居板的数据）
            for f in frames:
                self.reads += 1
                if len(f) >= 12 and f[4] == 0x00:
                    uid = f[7:11].hex().upper()
                    ctype = f[5:7].hex().upper()
                    now = time.time()
                    if uid != self.last_uid or now - self.last_ts > self.debounce:
                        self.last_uid, self.last_ts = uid, now
                        self.log("[rfid] card uid=%s type=%s" % (uid, ctype))
                        try:
                            self.on_card(uid, ctype)
                        except Exception as e:
                            self.log("[rfid] callback error: %s" % e)
            time.sleep(0.15)

    def status(self):
        return {"transport": "serial", "port": self.port, "baud": self.baud,
                "online": self.online, "reads": self.reads, "last_uid": self.last_uid}
