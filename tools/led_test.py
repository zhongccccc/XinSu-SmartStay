#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""点灯测试：全亮 6 秒，再灭。"""
import os
import time
import termios


def open_port():
    fd = os.open("/dev/ttyUSB2", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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


fd = open_port()
print(">>> 全部 12 颗灯点亮 6 秒")
os.write(fd, b"zk led 0xFFF\r")
time.sleep(6)
print(">>> 熄灭")
os.write(fd, b"zk ledoff\r")
time.sleep(1)
os.close(fd)
print(">>> 完成")
