#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZDG 身份证读卡器（hid2com 桥）帧格式试探。

从设备回显看：首字节是"报告类型"，0x00 被判非法（usb report type error!）。
这里枚举 类型字节 × 帧体 的组合，看哪种能拿到有效应答。
"""
import os
import select
import time

DEV = "/dev/hidraw2"


def fmt(b):
    return " ".join("%02X" % x for x in b[:32])


def drain(fd, secs=1.2):
    out = []
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.15)
        if not r:
            continue
        try:
            d = os.read(fd, 4096)
        except BlockingIOError:
            continue
        if d:
            out.append(d)
    return out


def payload_str(d):
    try:
        s = d.decode("ascii", "ignore").strip("\x00").strip()
        if s and all(32 <= ord(c) < 127 or c in "\r\n\t" for c in s):
            return s
    except Exception:
        pass
    return ""


# 华视/通用二代证 寻卡/选卡/读卡 串口帧（不含外层类型字节）
BODIES = {
    "寻卡 96 69 05 08": bytes.fromhex("aaaaaa96690508") + b"\x00" * 9,
    "寻卡 96 69 05 09": bytes.fromhex("aaaaaa96690509") + b"\x00" * 9,
    "读卡 96 69 05 0A": bytes.fromhex("aaaaaa9669050a") + b"\x00" * 9,
    "选卡 96 69 05 0B": bytes.fromhex("aaaaaa9669050b") + b"\x00" * 9,
    "查状态 96 69 05 00": bytes.fromhex("aaaaaa96690500") + b"\x00" * 9,
}

TYPES = [0x01, 0x02, 0x03, 0x05, 0x10]

fd = os.open(DEV, os.O_RDWR | os.O_NONBLOCK)
drain(fd, 0.5)

for tname, body in BODIES.items():
    for t in TYPES:
        frame = bytes([t]) + body
        frame = frame + b"\x00" * (64 - len(frame))
        try:
            os.write(fd, frame)
        except OSError as e:
            print("type=%02X %-20s write err %s" % (t, tname, e))
            continue
        resp = drain(fd, 0.9)
        if resp:
            for r in resp:
                txt = payload_str(r)
                print("type=%02X %-20s IN %s %s" % (t, tname, fmt(r), ("| " + txt) if txt else ""))
        else:
            print("type=%02X %-20s --" % (t, tname))

os.close(fd)
