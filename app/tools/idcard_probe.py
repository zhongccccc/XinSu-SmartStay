#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZDG 身份证读卡器探测：自动找 hidraw 节点，按 [长度][数据] 发指令，抓全部应答。"""
import glob
import os
import select
import time


def find_idreader():
    best = None
    for h in sorted(glob.glob("/dev/hidraw*")):
        name = ""
        try:
            with open("/sys/class/hidraw/%s/device/uevent" % h.rsplit("/", 1)[-1],
                      encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("HID_NAME="):
                        name = line.split("=", 1)[1].strip()
        except Exception:
            pass
        print("  %-16s %s" % (h, name))
        if "id reader" in name.lower() or "zdg" in name.lower():
            best = h
    return best


def fmt(b, n=48):
    return " ".join("%02X" % x for x in b[:n])


def drain(fd, secs=0.9):
    out = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                out += os.read(fd, 4096)
            except BlockingIOError:
                pass
    return out


def wrap(data):
    b = bytes([len(data)]) + data
    return b + b"\x00" * (64 - len(b))


CMDS = [
    ("SELECT 60 02", bytes.fromhex("00a40000026002")),
    ("GET-CHALLENGE", bytes.fromhex("0084000008")),
    ("READ-BINARY 8", bytes.fromhex("00b0000008")),
    ("SDT 寻卡 96 69 05 08", bytes.fromhex("aaaaaa96690508") + b"\x00" * 9),
    ("SDT 选卡 96 69 05 09", bytes.fromhex("aaaaaa96690509") + b"\x00" * 9),
    ("SDT 读卡 96 69 05 0A", bytes.fromhex("aaaaaa9669050a") + b"\x00" * 9),
    ("SDT 复位 96 69 05 01", bytes.fromhex("aaaaaa96690501") + b"\x00" * 9),
]

print("=== 查找读卡器 ===")
dev = find_idreader()
print("使用:", dev or "未找到")
if not dev:
    raise SystemExit(1)

fd = os.open(dev, os.O_RDWR | os.O_NONBLOCK)
drain(fd, 0.5)

print("=" * 70)
for name, data in CMDS:
    os.write(fd, wrap(data))
    resp = drain(fd, 1.0)
    txt = ""
    if resp:
        s = bytes(c for c in resp if 32 <= c < 127).decode("ascii", "ignore").strip()
        txt = " | " + s[:50] if s and len(s) > 3 else ""
    print("%-22s -> %s%s" % (name, fmt(resp) if resp else "(无应答)", txt))
    time.sleep(0.2)

print("=" * 70)
print("连续三次 寻卡：")
for i in range(3):
    os.write(fd, wrap(bytes.fromhex("aaaaaa96690508") + b"\x00" * 9))
    resp = drain(fd, 1.0)
    print("  #%d %s" % (i + 1, fmt(resp) if resp else "(无应答)"))
    time.sleep(0.3)

os.close(fd)
