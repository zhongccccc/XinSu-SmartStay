# -*- coding: utf-8 -*-
"""键盘型 HID 外设（二维码识别器 / RFID 读卡器）抓取。

原理：这类设备在 Linux 下表现为 USB HID keyboard，直接向系统注入按键。
本模块用 evdev 原始事件读取 + EVIOCGRAB 独占，把输入的字符流还原成
"一次完整扫描"（回车或 350ms 静默作为结束符），再从界面/业务层路由，
避免扫码内容落到浏览器输入框里。
"""
import fcntl
import glob
import os
import re
import select
import struct
import threading
import time

EV_SYN, EV_KEY, EV_MSC = 0, 1, 4
EVIOCGRAB = 0x40044590
EVENT_FMT = "llHHi"
EVENT_SIZE = struct.calcsize(EVENT_FMT)

KEYMAP = {
    2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9", 11: "0",
    12: "-", 13: "=", 15: "\t",
    16: "q", 17: "w", 18: "e", 19: "r", 20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p",
    30: "a", 31: "s", 32: "d", 33: "f", 34: "g", 35: "h", 36: "j", 37: "k", 38: "l",
    39: ";", 40: "'", 43: "\\",
    44: "z", 45: "x", 46: "c", 47: "v", 48: "b", 49: "n", 50: "m",
    51: ",", 52: ".", 53: "/", 57: " ",
}
KEY_ENTER, KEY_KPENTER, KEY_LEFTSHIFT, KEY_RIGHTSHIFT = 28, 96, 42, 54


def _sysfs(path, name, default=""):
    """path 形如 /dev/input/event3，映射到 /sys/class/input/event3/..."""
    base = path.replace("/dev/input/", "/sys/class/input/")
    try:
        with open(os.path.join(base, name), "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return default


def _has_key(path, code):
    """检查 sysfs 键盘能力位图里是否含某个 key code。"""
    caps = _sysfs(path, "device/capabilities/key")
    if not caps:
        return False
    try:
        bits = int(caps.replace(" ", ""), 16)
        return bool((bits >> code) & 1)
    except Exception:
        return False


class InputDevice:
    def __init__(self, path):
        self.path = path
        self.name = _sysfs(path, "device/name") or os.path.basename(path)
        self.uniq = _sysfs(path, "device/uniq")
        self.phys = _sysfs(path, "device/phys")
        self.grabbable = _has_key(path, KEY_ENTER) and _has_key(path, 2)

    def __repr__(self):
        return "<%s %s>" % (self.path, self.name)


def list_input_devices():
    out = []
    for ev in sorted(glob.glob("/dev/input/event*"), key=lambda p: int(p.rsplit("event", 1)[-1])):
        try:
            out.append(InputDevice(ev))
        except Exception:
            pass
    return out


def classify(name):
    n = (name or "").lower()
    if any(k in n for k in ("rfid", "读卡", "ic card", "iccard", "nfc", "card reader")):
        return "rfid"
    if any(k in n for k in ("barcode", "bar code", "scanner", "扫码", "二维码", "qr")):
        return "qr"
    if any(k in n for k in ("pos", "payment")):
        return "qr"
    return None


class ScannerHub:
    """监听所有键盘型输入设备，识别并独占其中的扫码/读卡设备。"""

    def __init__(self, on_scan, extra_names=None, name_re="", log=print):
        self.on_scan = on_scan
        self.log = log
        self.extra = [s.lower() for s in (extra_names or [])]
        self.re = re.compile(name_re) if name_re else None
        self._workers = {}
        self._stop = False
        self._lock = threading.Lock()
        self.devices = []

    def start(self):
        threading.Thread(target=self._watch, name="hid-watch", daemon=True).start()

    def stop(self):
        self._stop = True

    def _watch(self):
        while not self._stop:
            try:
                self.refresh()
            except Exception as e:
                self.log("[hid] watch error: %s" % e)
            time.sleep(2)

    def refresh(self):
        cur = {d.path for d in list_input_devices()}
        with self._lock:
            for path in list(self._workers):
                if path not in cur:
                    self._workers.pop(path)
        for d in list_input_devices():
            kind = self._kind_of(d)
            if kind and d.path not in self._workers:
                self._workers[d.path] = True
                threading.Thread(target=self._reader, args=(d, kind), daemon=True,
                                 name="hid-%s" % os.path.basename(d.path)).start()
        self.devices = [{"path": d.path, "name": d.name, "kind": self._kind_of(d) or "other",
                         "grabbed": d.path in self._workers} for d in list_input_devices()]

    def _kind_of(self, d):
        k = classify(d.name)
        if k:
            return k
        low = d.name.lower()
        if any(s in low for s in self.extra):
            return "qr"
        if self.re and self.re.search(d.name):
            return "qr"
        return None

    def _reader(self, dev, kind):
        fd = None
        try:
            fd = os.open(dev.path, os.O_RDONLY | os.O_NONBLOCK)
            grabbed = False
            try:
                fcntl.ioctl(fd, EVIOCGRAB, 1)
                grabbed = True
            except Exception as e:
                self.log("[hid] grab %s failed: %s" % (dev.name, e))
            self.log("[hid] capture %s (%s) grabbed=%s" % (dev.name, kind, grabbed))
            buf, last = [], 0.0
            while not self._stop:
                r, _, _ = select.select([fd], [], [], 0.4)
                if not r:
                    if buf and time.time() - last > 0.35:
                        self._emit(dev, kind, "".join(buf))
                        buf, last = [], 0.0
                    continue
                try:
                    data = os.read(fd, EVENT_SIZE * 64)
                except BlockingIOError:
                    continue
                for i in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
                    _, _, etype, code, value = struct.unpack(EVENT_FMT, data[i:i + EVENT_SIZE])
                    if etype != EV_KEY or value != 1:
                        continue
                    if code in (KEY_ENTER, KEY_KPENTER):
                        if buf:
                            self._emit(dev, kind, "".join(buf))
                        buf, last = [], 0.0
                        continue
                    ch = KEYMAP.get(code)
                    if ch:
                        buf.append(ch)
                        last = time.time()
        except Exception as e:
            self.log("[hid] reader %s exited: %s" % (dev.name, e))
        finally:
            try:
                if fd is not None:
                    os.close(fd)
            except Exception:
                pass
            with self._lock:
                self._workers.pop(dev.path, None)

    def _emit(self, dev, kind, text):
        code = text.strip()
        if len(code) < 3:
            return
        self.log("[hid] scan %s <- %r" % (kind, code))
        try:
            self.on_scan(code, kind, dev.name)
        except Exception as e:
            self.log("[hid] on_scan error: %s" % e)
