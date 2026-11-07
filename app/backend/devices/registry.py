# -*- coding: utf-8 -*-
"""USB / 输入设备 / 串口 扫描，用于前端设备状态灯与外设自检。"""
import glob
import os
import re
import time

from ..config import CONF


def _read(p, default=""):
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return default


def usb_devices():
    out = []
    for d in glob.glob("/sys/bus/usb/devices/*"):
        vid = _read(os.path.join(d, "idVendor"))
        pid = _read(os.path.join(d, "idProduct"))
        if not vid or not pid:
            continue
        out.append({
            "vid": vid, "pid": pid,
            "id": "%s:%s" % (vid, pid),
            "product": _read(os.path.join(d, "product")),
            "manufacturer": _read(os.path.join(d, "manufacturer")),
            "serial": _read(os.path.join(d, "serial")),
        })
    return out


def input_devices():
    out = []
    for ev in sorted(glob.glob("/dev/input/event*"), key=lambda p: int(p.rsplit("event", 1)[-1])):
        base = ev.replace("/dev/input/", "/sys/class/input/")
        name = _read(os.path.join(base, "device", "name"))
        caps = _read(os.path.join(base, "device", "capabilities", "abs"))
        out.append({"path": ev, "name": name or os.path.basename(ev), "has_abs": bool(caps and caps.strip("0"))})
    return out


def serial_ports():
    return sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))


def audio_cards():
    return _read("/proc/asound/cards")


class DeviceRegistry:
    def __init__(self, camera, audio, lock, scanner, rfid=None, cfg=None):
        self.camera = camera
        self.audio = audio
        self.lock = lock
        self.scanner = scanner
        self.rfid = rfid
        self.cfg = cfg or CONF
        self._last = None
        self._ts = 0

    def snapshot(self, force=False):
        if not force and self._last and time.time() - self._ts < 2:
            return self._last
        usb = usb_devices()
        ins = input_devices()
        serial = serial_ports()
        audio_ok = bool(audio_cards())
        touch = [d for d in ins if d["has_abs"] and ("ts" in d["name"].lower()
                                                     or "touch" in d["name"].lower())]
        hid_kinds = {"qr": [], "rfid": []}
        for d in getattr(self.scanner, "devices", []):
            if d["kind"] in hid_kinds:
                hid_kinds[d["kind"]].append(d["name"])

        # 身份证读卡器：优先按产品名识别（ZDG ID Reader 等），再按常见读卡器芯片 VID 兜底
        kw = ("id reader", "身份证", "id card", "读卡", "zdg", "resident", "identity")
        idcard = [u for u in usb
                  if any(k in (u["product"] + " " + u["manufacturer"]).lower() for k in kw)]
        if not idcard:
            idcard = [u for u in usb if u["vid"] in ("0bda", "2e3c", "0483")
                      and "hub" not in u["product"].lower()]

        cam = self.camera.info()
        lock = self.lock.status()
        rfid_ok = bool(self.rfid and self.rfid.status().get("online"))
        rfid_detail = (("串口 %s" % self.rfid.port) if rfid_ok else
                       (hid_kinds["rfid"][0] if hid_kinds["rfid"] else "未接入"))
        items = [
            {"key": "screen", "label": "触摸屏", "present": bool(touch) or cam["ok"],
             "detail": (touch[0]["name"] if touch else "DSI 面板")},
            {"key": "camera", "label": "摄像头", "present": cam["ok"],
             "detail": cam["name"] or cam["node"] or "未识别"},
            {"key": "idcard", "label": "身份证", "present": bool(idcard),
             "detail": idcard[0]["product"] if idcard else "未接入"},
            {"key": "rfid", "label": "房卡读写", "present": rfid_ok or bool(hid_kinds["rfid"]),
             "detail": rfid_detail},
            {"key": "qr", "label": "扫码支付", "present": bool(hid_kinds["qr"]),
             "detail": hid_kinds["qr"][0] if hid_kinds["qr"] else "未接入"},
            {"key": "audio", "label": "音响/麦克风", "present": audio_ok,
             "detail": (audio_cards().splitlines() or ["无声卡"])[0].strip() if audio_ok else "无声卡"},
            {"key": "lock", "label": "智能门锁", "present": lock.get("online", False),
             "detail": lock.get("transport", "mock")},
        ]
        snap = {"ts": time.time(), "items": items, "usb": usb, "serial": serial,
                "input": ins, "raw_audio": audio_cards()}
        self._last, self._ts = snap, time.time()
        return snap
