#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测门锁板端口并写回配置。"""
import glob
import json
import os
import select
import termios
import time


def open_port(dev):
    fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def drain(fd):
    try:
        while os.read(fd, 8192):
            pass
    except BlockingIOError:
        pass


def read_for(fd, secs):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.12)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf


dev = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    fd = open_port(p)
    time.sleep(0.2)
    drain(fd)
    os.write(fd, b"zk ping\r")
    buf = read_for(fd, 2.2)
    os.close(fd)
    txt = buf.decode("utf-8", "ignore")
    if "ZK|ACK|PING" in txt:
        line = [l for l in txt.splitlines() if "PING" in l][0]
        print("板子:", p, line.strip()[:90])
        dev = p
        break
    print("跳过:", p)

if not dev:
    print("!! 没有任何端口响应门锁协议")
    raise SystemExit(1)

cfg = '/opt/zhikong/etc/config.json'
d = json.load(open(cfg))
d['devices']['lock'].update({"transport": "board", "port": dev, "baud": 115200})
json.dump(d, open(cfg, 'w'), ensure_ascii=False, indent=2)
print("配置已更新为:", dev)
