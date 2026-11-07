#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""持续轮询 ZDG 读卡器：卡一放上去就把应答抓到日志里。

帧格式（已由试验确定）：64 字节 HID 报告 = [长度][APDU...][0x00 填充]
"""
import os
import select
import sys
import time

DEV = "/dev/hidraw2"
LOG = "/opt/zhikong/data/idpoll.log"
SECS = int(sys.argv[1]) if len(sys.argv) > 1 else 300

# 二代证常见 APDU 序列
CMDS = [
    ("SELECT-EF", bytes.fromhex("00a40000026002")),
    ("GET-CHALLENGE", bytes.fromhex("0084000008")),
    ("READ-BINARY", bytes.fromhex("00b0000008")),
]


def log(s):
    line = "%s %s" % (time.strftime("%H:%M:%S"), s)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def drain(fd, secs=0.5):
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


def ascii_of(b):
    s = "".join(chr(c) if 32 <= c < 127 else "." for c in b)
    return s.rstrip(".").strip()


fd = os.open(DEV, os.O_RDWR | os.O_NONBLOCK)
drain(fd, 0.3)
log("=== poll start, %ds ===" % SECS)
end = time.time() + SECS
last = b""
n = 0
while time.time() < end:
    n += 1
    for name, apdu in CMDS:
        frame = bytes([len(apdu)]) + apdu
        frame += b"\x00" * (64 - len(frame))
        try:
            os.write(fd, frame)
        except OSError as e:
            log("write err %s" % e)
            time.sleep(1)
            continue
        resp = drain(fd, 0.6)
        if resp and resp != last:
            last = resp
            log("%-13s IN %s | %s" % (name, resp[:32].hex(" "), ascii_of(resp[:40])))
    time.sleep(0.8)
log("=== poll end, %d rounds ===" % n)
os.close(fd)
