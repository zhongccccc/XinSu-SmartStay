#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""閫氳繃 uinput 娉ㄥ叆涓€娆¤Е鎽哥偣鍑伙紝鐢ㄤ簬楠岃瘉鏁存潯瑙︽懜閾捐矾锛堥┍鍔ㄢ啋鍚堟垚鍣ㄢ啋娴忚鍣級銆?
鐢ㄦ硶: sudo python3 touch_test.py <x> <y>
浣跨敤浼犵粺 uinput_user_dev 鎺ュ彛锛屽吋瀹规€ф渶濂姐€?"""
import ctypes
import fcntl
import os
import struct
import sys
import time

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_PROPBIT = 0x40045566
UI_SET_ABSBIT = 0x40045567
INPUT_PROP_DIRECT = 0x01
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
ABS_CNT = 0x40
ABS_X, ABS_Y = 0x00, 0x01
ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID = 0x2F, 0x35, 0x36, 0x39
BTN_TOUCH = 0x14A
SYN_REPORT = 0


class InputId(ctypes.Structure):
    _fields_ = [("bustype", ctypes.c_uint16), ("vendor", ctypes.c_uint16),
                ("product", ctypes.c_uint16), ("version", ctypes.c_uint16)]


class UserDev(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char * 80), ("id", InputId),
                ("ff_effects_max", ctypes.c_uint32),
                ("absmax", ctypes.c_int32 * ABS_CNT), ("absmin", ctypes.c_int32 * ABS_CNT),
                ("absfuzz", ctypes.c_int32 * ABS_CNT), ("absflat", ctypes.c_int32 * ABS_CNT)]


def emit(fd, etype, code, value):
    os.write(fd, struct.pack("llHHi", 0, 0, etype, code, value))


def main():
    x, y = int(sys.argv[1]), int(sys.argv[2])
    W, H = 800, 480
    fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)

    for ev in (EV_SYN, EV_KEY, EV_ABS):
        fcntl.ioctl(fd, UI_SET_EVBIT, ev)
    fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_TOUCH)
    fcntl.ioctl(fd, UI_SET_PROPBIT, INPUT_PROP_DIRECT)
    for code in (ABS_X, ABS_Y, ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y,
                 ABS_MT_TRACKING_ID):
        fcntl.ioctl(fd, UI_SET_ABSBIT, code)

    dev = UserDev()
    dev.name = b"zhikong-touch-test"
    dev.id = InputId(0x03, 0x1234, 0x5678, 1)
    dev.absmin[ABS_X], dev.absmax[ABS_X] = 0, W - 1
    dev.absmin[ABS_Y], dev.absmax[ABS_Y] = 0, H - 1
    dev.absmin[ABS_MT_SLOT], dev.absmax[ABS_MT_SLOT] = 0, 9
    dev.absmin[ABS_MT_POSITION_X], dev.absmax[ABS_MT_POSITION_X] = 0, W - 1
    dev.absmin[ABS_MT_POSITION_Y], dev.absmax[ABS_MT_POSITION_Y] = 0, H - 1
    dev.absmin[ABS_MT_TRACKING_ID], dev.absmax[ABS_MT_TRACKING_ID] = 0, 65535
    os.write(fd, bytes(dev))
    fcntl.ioctl(fd, UI_DEV_CREATE)
    time.sleep(float(os.environ.get("ZK_HOLD", "1.0")))

    taps = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.06   # 秒，长按就传 1.8
    for n in range(taps):
        emit(fd, EV_ABS, ABS_MT_SLOT, 0)
        emit(fd, EV_ABS, ABS_MT_TRACKING_ID, n + 1)
        emit(fd, EV_ABS, ABS_MT_POSITION_X, x)
        emit(fd, EV_ABS, ABS_MT_POSITION_Y, y)
        emit(fd, EV_ABS, ABS_X, x)
        emit(fd, EV_ABS, ABS_Y, y)
        emit(fd, EV_KEY, BTN_TOUCH, 1)
        emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(hold)
        emit(fd, EV_ABS, ABS_MT_TRACKING_ID, -1)
        emit(fd, EV_KEY, BTN_TOUCH, 0)
        emit(fd, EV_SYN, SYN_REPORT, 0)
        if n + 1 < taps:
            time.sleep(0.12)          # 双击间隔
    time.sleep(0.5)

    fcntl.ioctl(fd, UI_DEV_DESTROY)
    os.close(fd)
    print("tap %d,%d x%d injected" % (x, y, taps))


if __name__ == "__main__":
    main()
