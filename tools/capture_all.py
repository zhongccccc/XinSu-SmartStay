#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同时监听所有串口，抓智能家居板开机日志。"""
import glob
import os
import select
import termios
import time

DEVS = sorted(glob.glob("/dev/ttyUSB*"))
fds = {}
for d in DEVS:
    try:
        fd = os.open(d, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception:
        continue
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    fds[d] = fd

bufs = {d: b"" for d in fds}
end = time.time() + 55
while time.time() < end:
    rl, _, _ = select.select(list(fds.values()), [], [], 0.2)
    for fd in rl:
        name = [k for k, v in fds.items() if v == fd][0]
        try:
            bufs[name] += os.read(fd, 8192)
        except BlockingIOError:
            pass

for fd in fds.values():
    os.close(fd)

out = []
for d in DEVS:
    if d not in bufs:
        continue
    txt = bufs[d].decode("utf-8", "ignore")
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    out.append("=== %s : %d 字节 / %d 行 ===" % (d, len(bufs[d]), len(lines)))
    for l in lines[-25:]:
        out.append("  | " + l[:100])
    out.append("")

open("/tmp/home_boot_all.txt", "w").write("\n".join(out))
print("\n".join(out))
