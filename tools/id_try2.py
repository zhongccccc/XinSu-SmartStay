#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按"首字节=长度"的假设再试 ZDG 读卡器。"""
import os
import select
import time

DEV = "/dev/hidraw2"
BODY = {
    "寻卡 AA..96 69 05 08": bytes.fromhex("aaaaaa9669050800"),
    "读卡 AA..96 69 05 0A": bytes.fromhex("aaaaaa9669050a00"),
    "选卡 AA..96 69 05 0B": bytes.fromhex("aaaaaa9669050b00"),
    "查状态 96 69 05 00": bytes.fromhex("aaaaaa9669050000"),
    "APDU 006002": bytes.fromhex("00a40000026002"),
    "APDU GETCH": bytes.fromhex("0084000008"),
}


def fmt(b):
    return " ".join("%02X" % x for x in b[:24])


def drain(fd, secs=1.0):
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


fd = os.open(DEV, os.O_RDWR | os.O_NONBLOCK)
drain(fd, 0.4)

for name, body in BODY.items():
    for prefix in (len(body), len(body) + 1, 0x40):
        frame = bytes([prefix]) + body
        frame += b"\x00" * (64 - len(frame))
        try:
            os.write(fd, frame)
        except OSError as e:
            print("%-22s len=%02X write err %s" % (name, prefix, e))
            continue
        resp = drain(fd, 0.9)
        for r in resp:
            print("%-22s len=%02X IN %s" % (name, prefix, fmt(r)))
        if not resp:
            print("%-22s len=%02X --" % (name, prefix))
os.close(fd)
