#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HID 原始报文工具：抓包 / 试探命令。

用法：
  python3 hid_probe.py dump  /dev/hidraw2 20          # 抓 20 秒未请求的上报（放证时用）
  python3 hid_probe.py probe /dev/hidraw2             # 依次发候选命令帧，打印应答
  python3 hid_probe.py send  /dev/hidraw2 aaaa...     # 发一帧（hex），等 2 秒收应答
"""
import os
import select
import sys
import time

PATH = "/opt/zhikong/data/hid_capture.log"


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def fmt(data):
    return " ".join("%02X" % b for b in data)


def open_dev(dev):
    fd = os.open(dev, os.O_RDWR | os.O_NONBLOCK)
    return fd


def drain(fd, seconds):
    """读走所有 pending 上报，返回列表。"""
    out = []
    end = time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if not r:
            continue
        try:
            data = os.read(fd, 4096)
        except BlockingIOError:
            continue
        except OSError as e:
            log("read error: %s" % e)
            break
        if data:
            out.append(data)
    return out


def cmd_dump(dev, secs):
    fd = open_dev(dev)
    log("dump %s for %ss ..." % (dev, secs))
    end = time.time() + secs
    n = 0
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.3)
        if not r:
            continue
        try:
            data = os.read(fd, 4096)
        except BlockingIOError:
            continue
        if data:
            n += 1
            log("IN  len=%d  %s" % (len(data), fmt(data[:64])))
    log("dump end, %d report(s)" % n)
    os.close(fd)


def send_frame(fd, payload, wait=1.5):
    if len(payload) < 64:
        payload = payload + b"\x00" * (64 - len(payload))
    payload = payload[:64]
    try:
        os.write(fd, payload)
        log("OUT %s" % fmt(payload[:16]))
    except OSError as e:
        log("write error: %s" % e)
        return []
    return drain(fd, wait)


def cmd_send(dev, hexstr):
    fd = open_dev(dev)
    payload = bytes.fromhex(hexstr)
    resp = send_frame(fd, payload)
    if not resp:
        log("no response")
    for r in resp:
        log("IN  %s" % fmt(r[:64]))
    os.close(fd)


# 华视 / 通用二代证读卡器常见帧头试探（64 字节 report）
CANDIDATES = [
    ("寻卡 AA..96 69 05 08", "aaaaaa96690508" + "00" * 9),
    ("寻卡 AA..96 69 05 09", "aaaaaa96690509" + "00" * 9),
    ("读卡 AA..96 69 05 0A", "aaaaaa9669050a" + "00" * 9),
    ("读卡 AA..96 69 05 0B", "aaaaaa9669050b" + "00" * 9),
    ("寻卡 AA..96 69 05 30", "aaaaaa96690530" + "00" * 9),
    ("复位 AA..96 69 05 01", "aaaaaa96690501" + "00" * 9),
    ("全零", "00" * 16),
    ("AA 55 00 00", "aa550000" + "00" * 12),
]


def cmd_probe(dev):
    fd = open_dev(dev)
    log("=== probe %s ===" % dev)
    for name, hx in CANDIDATES:
        payload = bytes.fromhex(hx)
        try:
            os.write(fd, payload + b"\x00" * (64 - len(payload)))
        except OSError as e:
            log("%-28s write error: %s" % (name, e))
            continue
        resp = drain(fd, 1.0)
        if resp:
            for r in resp:
                log("%-28s IN  %s" % (name, fmt(r[:64])))
        else:
            log("%-28s -- no response" % name)
    os.close(fd)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mode, dev = sys.argv[1], sys.argv[2]
    if mode == "dump":
        cmd_dump(dev, int(sys.argv[3]) if len(sys.argv) > 3 else 15)
    elif mode == "probe":
        cmd_probe(dev)
    elif mode == "send":
        cmd_send(dev, sys.argv[3])
    else:
        print(__doc__)
