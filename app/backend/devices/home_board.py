# -*- coding: utf-8 -*-
"""智能家居板（通晓 TX-SMART-R / RK2206）串口驱动。

板子固件把协议注册成 OHOS shell 子命令 `zh`：

    K1 发送：  zh ping / zh env / zh pir / zh gas
               zh light on|off / zh fan on|off|1-99 / zh beep <ms>

    板子回：    ZH|ACK|PING|OK|rk2206-home-v17|...
               ZH|ACK|ENV|OK|t=28.8|h=57.6|lux=112
               ZH|EVT|PIR|1        （人体感应变化）
               ZH|EVT|KEY|6        （板载按键）
               ZH|EVT|LIGHT|off

本驱动负责：
- 自动找板子（遍历 /dev/ttyUSB* 发 `zh ping`）
- 轮询环境数据（默认 5 秒）
- 把 EVT 事件回调给上层
"""
import glob
import os
import re
import select
import termios
import threading
import time

SPEEDS = {9600: termios.B9600, 19200: termios.B19200, 38400: termios.B38400,
          57600: termios.B57600, 115200: termios.B115200}


def _open_serial(port, baud=115200):
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = SPEEDS.get(baud, termios.B115200)
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


class HomeBoard:
    """一块板子一个实例，线程里轮询。"""

    def __init__(self, port=None, baud=115200, on_event=None, log=print, poll=5.0,
                 sim=False):
        self.sim = bool(sim)
        self.port = port
        self._fixed_port = True   # 永不扫描，只用给定端口
        self.baud = baud
        self.on_event = on_event
        self.log = log
        self.poll = poll
        self.online = False
        self.firmware = None
        self.data = {"temp": None, "hum": None, "lux": None, "gas": None, "pir": 0,
                     "light": 0, "fan": 0}
        self._fd = None
        self._buf = b""
        self._buffer_text = ""
        self._lock = threading.Lock()
        self._stop = False
        self._thread = None
        self._last_probe = 0.0
        self.last_error = ""

    # ---------------- 串口 ----------------
    def _open(self, port):
        try:
            self._fd = _open_serial(port, self.baud)
            self._buf = b""
            return True
        except OSError as e:
            self.last_error = "打开 %s 失败: %s" % (port, e)
            self._fd = None
            return False

    def _write(self, text):
        if self._fd is None:
            return False
        try:
            os.write(self._fd, (text + "\r").encode())
            return True
        except OSError:
            self._close()
            return False

    def _close(self):
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def _read(self, seconds):
        if self._fd is None:
            return ""
        out = b""
        end = time.time() + seconds
        while time.time() < end:
            try:
                r, _, _ = select.select([self._fd], [], [], 0.1)
            except (OSError, ValueError):
                break
            if r:
                try:
                    chunk = os.read(self._fd, 8192)
                except BlockingIOError:
                    chunk = b""
                except OSError:
                    break
                if chunk:
                    out += chunk
        return out.decode("utf-8", "ignore")

    # ---------------- 发现 ----------------
    def discover(self):
        """遍历串口，找应答 zh ping 的那块。"""
        if self._fixed_port and self.port:
            cand = [self.port]          # 固定端口：只探这一个，不打扰别的设备
        else:
            cand = list(sorted(glob.glob("/dev/ttyUSB*"))) + list(sorted(glob.glob("/dev/ttyACM*")))
        for port in cand:
            if not port:
                continue
            if not self._open(port):
                continue
            # 丢掉残留
            self._read(0.3)
            text = ""
            for _try in range(2):
                if not self._write("zh ping"):
                    break
                text = self._read(2.2)
                if "ZH|ACK|PING" in text:
                    break
            # ping 没回应时：板子若在自发心跳/事件，也认（应用活着但 shell 可能挂了）
            if "ZH|ACK|PING" not in text:
                text += self._read(3.5)
            if ("ZH|ACK|PING" in text) or ("[zh] alive" in text) or ("ZH|EVT|" in text):
                m = re.search(r"ZH\|ACK\|PING\|OK\|([^|\r\n]+)", text)
                self.firmware = m.group(1).strip() if m else "heartbeat"
                self.port = port
                self.online = True
                self.last_error = ""
                self.log("[home] 找到板子 %s (%s)" % (port, self.firmware))
                return True
            self._close()
        self.online = False
        self.port = None
        self.last_error = "未找到 zh 板子"
        return False

    # ---------------- 命令 ----------------
    def command(self, text, wait=1.6):
        with self._lock:
            if self._fd is None:
                if not self.discover():
                    return ""
            self._read(0.05)
            if not self._write(text):
                self.online = False
                return ""
            return self._read(wait)

    def ping(self, wait=1.4):
        if self.sim:
            return True
        return "ZH|ACK|PING" in self.command("zh ping", wait)

    def read_env(self):
        """读温湿度/光照/燃气/人体，更新 self.data。"""
        text = self.command("zh env", 2.4)
        m = re.search(r"ZH\|ACK\|ENV\|(\w+)\|t=(-?[\d.]+)\|h=(-?[\d.]+)\|lux=(-?\d+)", text)
        if m:
            self.data["temp"] = float(m.group(2))
            self.data["hum"] = float(m.group(3))
            self.data["lux"] = int(m.group(4))
        self._read_gas()
        self._read_pir()
        return dict(self.data)

    def _read_gas(self):
        text = self.command("zh gas", 1.2)
        m = re.search(r"ZH\|ACK\|GAS\|(\d+)", text)
        if m:
            self.data["gas"] = int(m.group(1))

    def _read_pir(self):
        text = self.command("zh pir", 1.2)
        m = re.search(r"ZH\|ACK\|PIR\|(\d+)", text)
        if m:
            self.data["pir"] = int(m.group(1))

    def light(self, on):
        if self.sim:
            self.data["light"] = 1 if on else 0
            return True
        ok = "ZH|ACK|LIGHT" in self.command("zh light %s" % ("on" if on else "off"), 2.0)
        if ok:
            self.data["light"] = 1 if on else 0
        return ok

    def fan(self, duty):
        if isinstance(duty, bool):
            duty = 60 if duty else 0
        if self.sim:
            self.data["fan"] = int(duty)
            return True
        ok = "ZH|ACK|FAN" in self.command("zh fan %d" % int(duty), 2.0)
        if ok:
            self.data["fan"] = int(duty)
        return ok

    def apply_mode(self, mode):
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

    def beep(self, ms=150):
        if self.sim:
            return True
        return "ZH|ACK|BEEP" in self.command("zh beep %d" % int(ms), 2.5)

    # ---------------- 后台 ----------------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        target = self._loop_sim if self.sim else self._loop
        self._thread = threading.Thread(target=target, name="home-board", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        self._close()

    def _loop_sim(self):
        """模拟模式：按 10 秒节奏生成数据，便于无硬件演示。"""
        import random
        self.online = True
        self.firmware = "simulated"
        self.data.update({"temp": 26.5, "hum": 55.0, "lux": 180, "gas": 120,
                          "pir": 0, "light": 0, "fan": 0})
        n = 0
        while not self._stop:
            n += 1
            self.data["temp"] = round(self.data["temp"] + random.uniform(-0.15, 0.15), 1)
            self.data["hum"] = round(min(90, max(30, self.data["hum"] + random.uniform(-0.3, 0.3))), 1)
            self.data["lux"] = max(0, self.data["lux"] + random.randint(-8, 8))
            self.data["gas"] = max(30, self.data["gas"] + random.randint(-3, 3))
            if n % 6 == 0:
                before = self.data["pir"]
                self.data["pir"] = 0 if before else 1
                if self.on_event:
                    self.on_event({"type": "pir", "value": self.data["pir"]})
            time.sleep(10)
        return None

    def _loop(self):
        """被动监听板子的串口输出：

        固件每 10 秒打印一行心跳：
            [zh] alive #120 t=28.8 h=57.6 lux=112 gas=113 pir=0
        事件：
            ZH|EVT|PIR|1 / ZH|EVT|KEY|6 / ZH|EVT|LIGHT|off

        只有长时间没有心跳时才主动 ping 一次，避免把板子 shell 压垮。
        """
        last_rx = 0.0
        while not self._stop:
            try:
                if self._fd is None:
                    if not self.discover():
                        time.sleep(3.0)
                        continue
                    last_rx = time.time()

                chunk = self._read(0.6)
                if chunk:
                    last_rx = time.time()
                    self._buffer_text += chunk
                    # 按行切，保留最后半行
                    while "\n" in self._buffer_text:
                        line, self._buffer_text = self._buffer_text.split("\n", 1)
                        self._parse(line.strip("\r "))

                # 30 秒没心跳 → 认为掉线，重连探测
                if time.time() - last_rx > 30:
                    self.log("[home] 30 秒无心跳，重新探测")
                    self.online = False
                    self._close()
                    last_rx = time.time()
            except Exception as e:
                self.last_error = str(e)
                self.log("[home] 监听异常: %s" % e)
                self._close()
                time.sleep(2.0)

    # 心跳格式： [zh] alive #120 t=28.8 h=57.6 lux=112 gas=113 pir=0
    _RE_ALIVE = re.compile(
        r"t=(-?[\d.]+).*?h=(-?[\d.]+).*?lux=(-?\d+).*?gas=(-?\d+).*?pir=(\d)")

    def _parse(self, line):
        if not line:
            return
        if "alive" in line:
            m = self._RE_ALIVE.search(line)
            if m:
                before = dict(self.data)
                self.data["temp"] = float(m.group(1))
                self.data["hum"] = float(m.group(2))
                self.data["lux"] = int(m.group(3))
                self.data["gas"] = int(m.group(4))
                self.data["pir"] = int(m.group(5))
                self.online = True
                self.last_error = ""
                if self.data["pir"] != before.get("pir") and self.on_event:
                    self.on_event({"type": "pir", "value": self.data["pir"]})
                if self.data["gas"] != before.get("gas") and self.on_event:
                    self.on_event({"type": "gas", "value": self.data["gas"]})
            return

        if "ZH|EVT|" in line:
            m = re.search(r"ZH\|EVT\|(\w+)\|(\S+)", line)
            if m:
                kind, val = m.group(1), m.group(2)
                if kind == "PIR":
                    self.data["pir"] = 1 if val == "1" else 0
                    if self.on_event:
                        self.on_event({"type": "pir", "value": self.data["pir"]})
                elif kind == "LIGHT":
                    self.data["light"] = 0 if val == "off" else 1
                elif kind == "KEY" and self.on_event:
                    self.on_event({"type": "key", "value": val})
            return

        if "ZH|ACK|ENV" in line:
            m = re.search(r"t=(-?[\d.]+)\|h=(-?[\d.]+)\|lux=(-?\d+)", line)
            if m:
                self.data["temp"] = float(m.group(1))
                self.data["hum"] = float(m.group(2))
                self.data["lux"] = int(m.group(3))
                self.online = True

    def status(self):
        return {"online": bool(self.online), "port": self.port,
                "firmware": self.firmware, "data": dict(self.data),
                "error": self.last_error}
