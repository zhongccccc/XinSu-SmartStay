#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描局域网里开放的身份证读卡服务端口（7846 / 6045）。"""
import concurrent.futures as cf
import socket
import subprocess
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7846


def my_subnet():
    try:
        out = subprocess.run(["ip", "-4", "-o", "addr", "show"],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            if " wlan0 " in line or " eth" in line or " end" in line:
                for part in line.split():
                    if "/" in part and part[0].isdigit():
                        return part
    except Exception:
        pass
    return "10.243.222.40/24"


def probe(ip):
    s = socket.socket()
    s.settimeout(0.25)
    try:
        if s.connect_ex((ip, PORT)) == 0:
            return ip
    except Exception:
        pass
    finally:
        s.close()
    return None


cidr = my_subnet()
print("本机网段:", cidr)
base = ".".join(cidr.split(".")[:3])
ips = ["%s.%d" % (base, i) for i in range(1, 255)]
print("扫描 %s.* 的 %d 端口 …" % (base, PORT))

found = []
with cf.ThreadPoolExecutor(max_workers=96) as ex:
    for r in ex.map(probe, ips):
        if r:
            found.append(r)
            print("  开放:", r)
print("结果:", found or "无")
