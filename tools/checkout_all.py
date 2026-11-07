#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清空所有在住订单 + 清空门锁板上的凭证。"""
import os
import select
import sqlite3
import termios
import time
import urllib.request
import json

# 1) 数据库：全部置为已退房
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
n = c.execute("SELECT COUNT(*) FROM orders WHERE status='inhouse'").fetchone()[0]
c.execute("UPDATE orders SET status='checkedout', checkout_at=? WHERE status='inhouse'",
          (time.time(),))
c.commit()
c.close()
print("已退房 %d 单" % n)

# 2) 门锁板：清空凭证
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


fd = open_port('/dev/ttyUSB2')
time.sleep(0.2)
try:
    while os.read(fd, 8192):
        pass
except BlockingIOError:
    pass
os.write(fd, b"zk revoke\r")
time.sleep(1.0)
buf = b""
end = time.time() + 1.2
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.15)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
os.close(fd)
for line in buf.decode("utf-8", "ignore").splitlines():
    if "REVOKE" in line:
        print("门锁板:", line.strip()[:60])

# 3) 状态复位
req = urllib.request.Request('http://127.0.0.1:8080/api/cancel', data=b'{}',
                             headers={'Content-Type': 'application/json'})
urllib.request.urlopen(req).read()
print("系统已复位到待机")
