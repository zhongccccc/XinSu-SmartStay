#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门锁板模拟器 v2：连 shell 行为一起模拟（回显 + OHOS # 提示符 + 噪声）。

用法: python3 lock_board_sim.py --link /opt/zhikong/run/ttyLOCK

模拟内容：
  - 收到 "zk xxx" 回显一行，按协议回 ZK|ACK|...
  - 带 OHOS 风格提示符，验证 K1 侧的过滤能力（只认含 ZK| 的行）
  - 每 8 秒随机产生 KEY/CARD/DOOR 事件
"""
import os
import pty
import random
import select
import sys
import time
import tty

LINK = "/opt/zhikong/run/ttyLOCK"
for i, a in enumerate(sys.argv):
    if a == "--link" and i + 1 < len(sys.argv):
        LINK = sys.argv[i + 1]

master, slave = pty.openpty()
tty.setraw(slave)
name = os.ttyname(slave)
os.makedirs(os.path.dirname(LINK), exist_ok=True)
try:
    os.unlink(LINK)
except FileNotFoundError:
    pass
os.symlink(name, LINK)
print("模拟门锁板(shell 版)就绪: %s -> %s" % (LINK, name), flush=True)

valid = {"123456", "888888"}
buf = b""
last_evt = time.time()


def send(line):
    os.write(master, ("\r\nZK|" + line + "\r\n").encode())
    print("  -> ZK|" + line, flush=True)


os.write(master, b"\r\nOHOS # ")

while True:
    r, _, _ = select.select([master], [], [], 0.2)
    if r:
        try:
            chunk = os.read(master, 1024)
        except OSError:
            break
        buf += chunk
        while b"\r" in buf or b"\n" in buf:
            pos = [i for i in (buf.find(b"\r"), buf.find(b"\n")) if i >= 0]
            idx = min(pos)
            raw, buf = buf[:idx], buf[idx + 1:]
            line = raw.decode("utf-8", "ignore").strip()
            if not line:
                continue
            os.write(master, (line + "\r\n").encode())     # 回显
            print("  <- " + line, flush=True)
            parts = line.split()
            if parts and parts[0] == "zk":
                sub = parts[1] if len(parts) > 1 else ""
                if sub == "ping":
                    send("ACK|PING|OK|sim-shell-v2")
                elif sub == "issue" and len(parts) >= 6:
                    valid.add(parts[3])
                    send("ACK|ISSUE|OK|room=%s" % parts[2])
                elif sub == "open":
                    send("ACK|OPEN|OK")
                    send("EVT|DOOR|open")
                elif sub == "revoke":
                    valid.clear()
                    send("ACK|REVOKE|OK")
                elif sub == "code":
                    ok = len(parts) > 2 and parts[2] in valid
                    send("EVT|CODE|%s" % ("ok" if ok else "bad"))
                    if ok:
                        send("EVT|DOOR|open")
                else:
                    send("ACK|%s|ERR|unknown" % (sub or "?"))
            else:
                os.write(master, b"zk:command not found\r\n")
            os.write(master, b"OHOS # ")

    if time.time() - last_evt > 8:
        last_evt = time.time()
        kind = random.choice(["KEY", "CARD", "DOOR"])
        if kind == "KEY":
            send("EVT|KEY|1,2,3,*,0,#")
        elif kind == "CARD":
            send("EVT|CARD|0AD21E00")
        else:
            send("EVT|DOOR|close")
        os.write(master, b"OHOS # ")
