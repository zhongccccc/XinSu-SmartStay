#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""串口设备试探：监听 + 发 JSON ping + 常见帧，判断是不是门锁板。"""
import os
import select
import termios
import time
import tty

DEV = "/dev/ttyUSB0"


def setup(baud):
    fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    tty.setraw(fd)
    speed = {9600: termios.B9600, 19200: termios.B19200,
             57600: termios.B57600, 115200: termios.B115200}[baud]
    attrs = termios.tcgetattr(fd)
    attrs[4] = attrs[5] = speed
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd


def read_for(fd, secs):
    out = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                out += os.read(fd, 512)
            except BlockingIOError:
                pass
    return out


for baud in (115200, 9600):
    print("=== baud %d ===" % baud)
    try:
        fd = setup(baud)
    except Exception as e:
        print("open failed:", e)
        continue
    idle = read_for(fd, 2.0)
    print("被动监听 2s:", idle.hex(" ") if idle else "(无数据)")
    for name, frame in [
        ("json-ping", b'{"cmd":"ping"}\n'),
        ("at", b"AT\r\n"),
        ("hex-aa55", bytes.fromhex("aa5501000000")),
        ("modbus-read", bytes.fromhex("010300000001840a")),
    ]:
        os.write(fd, frame)
        resp = read_for(fd, 1.2)
        txt = ""
        try:
            s = resp.decode("ascii", "ignore").strip()
            if s:
                txt = "| " + s.replace("\n", "\\n")[:60]
        except Exception:
            pass
        print("  %-13s -> %s %s" % (name, resp.hex(" ") if resp else "(无应答)", txt))
    os.close(fd)
