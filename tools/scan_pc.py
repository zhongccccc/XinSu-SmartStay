#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在同一网段找 Windows 主机（445/3389/139）。"""
import concurrent.futures as cf
import socket

BASE = "10.243.222."
PORTS = [445, 3389, 139, 7846]


def probe(ip):
    hits = []
    for p in PORTS:
        s = socket.socket()
        s.settimeout(0.22)
        try:
            if s.connect_ex((ip, p)) == 0:
                hits.append(p)
        except Exception:
            pass
        finally:
            s.close()
    return (ip, hits) if hits else None


found = []
with cf.ThreadPoolExecutor(max_workers=128) as ex:
    for r in ex.map(probe, ["%s%d" % (BASE, i) for i in range(1, 255)]):
        if r:
            found.append(r)
            print("  %-16s 开放 %s" % (r[0], r[1]))
print("共 %d 台" % len(found))
