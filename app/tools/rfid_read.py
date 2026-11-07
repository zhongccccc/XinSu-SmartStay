#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RFID V23B 读卡器：扫描缓冲区里的合法帧并解析卡号。

帧格式（来自厂商 C++ 样例 + 手册）：
  发送： 01 08 A1 20 00 01 00 76        读卡号
  成功： TT 0C CC 20 00 <2B 卡类型> <4B 卡号> <校验>   校验 = ~XOR(前 n-1 字节)
  失败： TT 08 CC 20 01 00 00 <校验>
TT/CC 随卡类型略有不同（实测 ID 卡为 04/02），因此按「长度+校验」扫帧，不写死命令字。
"""
import os
import select
import sys
import termios
import time

DEV = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
LOOPS = int(sys.argv[3]) if len(sys.argv) > 3 else 5

SPEED = {9600: termios.B9600, 19200: termios.B19200, 38400: termios.B38400,
         57600: termios.B57600, 115200: termios.B115200}[BAUD]

CMD = bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])


def checksum_ok(buf):
    c = 0
    for b in buf[:-1]:
        c ^= b
    return buf[-1] == (~c) & 0xFF


def scan_frames(buf):
    """在字节流里找出所有校验通过的帧。"""
    out = []
    i = 0
    while i + 4 <= len(buf):
        n = buf[i + 1]
        if 4 <= n <= 32 and i + n <= len(buf):
            cand = buf[i:i + n]
            if checksum_ok(cand):
                out.append(cand)
                i += n
                continue
        i += 1
    return out


def parse(frame):
    """frame: TT 0C CC 20 00 type(2) id(4) ck"""
    if len(frame) >= 12 and frame[4] == 0x00:
        return {"ok": True, "type": frame[5:7].hex().upper(),
                "uid": frame[7:11].hex().upper()}
    if len(frame) >= 8:
        return {"ok": False, "status": frame[4] if len(frame) > 4 else None}
    return {"ok": False, "status": None}


def open_port():
    fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = 0
    a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = SPEED
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def main():
    fd = open_port()
    time.sleep(0.1)
    try:
        os.read(fd, 4096)          # 清掉上电时的垃圾数据
    except BlockingIOError:
        pass

    results = []
    for i in range(LOOPS):
        os.write(fd, CMD)
        buf = b""
        end = time.time() + 0.9
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                try:
                    buf += os.read(fd, 512)
                except BlockingIOError:
                    pass
        frames = scan_frames(buf)
        if frames:
            info = parse(frames[-1])
            print("第%d次: 帧=%s -> %s" % (i + 1, frames[-1].hex(" "),
                                          ("卡号 %s 类型 %s" % (info["uid"], info["type"]))
                                          if info["ok"] else "未检测到卡"))
            if info["ok"]:
                results.append(info)
        else:
            print("第%d次: 无合法帧 (收到 %d 字节: %s)" %
                  (i + 1, len(buf), buf[:24].hex(" ") if buf else "-"))
        time.sleep(0.25)
    os.close(fd)
    if results:
        print("\n最终卡号: %s" % results[-1]["uid"])
        print("卡类型  : %s" % results[-1]["type"])


if __name__ == "__main__":
    main()
