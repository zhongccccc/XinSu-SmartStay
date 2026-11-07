# -*- coding: utf-8 -*-
"""彻底禁止运行期扫描：家居板固定端口；没认领到就用配置里的端口。"""
import re

# ---------- HomeBoard：永不扫描 ----------
H = r"E:\zhikong\app\backend\devices\home_board.py"
h = open(H, encoding="utf-8").read()
if "self._fixed_port = True" not in h:
    h = h.replace("self._fixed_port = bool(port)", "self._fixed_port = True   # 永不扫描，只用给定端口")
    open(H, "w", encoding="utf-8").write(h)
    print("[home] 已禁止扫描")
else:
    print("[home] 已禁止扫描")

# ---------- main：home 端口兜底 ----------
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()
OLD = '_home_port = _ports.get("home") or _dev.get("home_port")'
NEW = '_home_port = _ports.get("home") or _dev.get("home_port") or "/dev/ttyUSB2"'
if OLD in s and '"/dev/ttyUSB2"' not in s.split("_home_port")[1][:80]:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[main] home 端口兜底已加")
else:
    print("[main] 状态:", "已存在" if '"/dev/ttyUSB2"' in s.split("_home_port")[1][:80] else "未匹配")

# ---------- lock：_reprobe 不再扫描（仅重试自己端口） ----------
L = r"E:\zhikong\app\backend\devices\lock.py"
l = open(L, encoding="utf-8").read()
OLD_RE = '''            found = self._scan_ports(self.baud)
            if found:
                from .lock_board import BoardLock
                self.port = found
                self._board = BoardLock(found, self.baud, on_event=self._on_evt, log=self.log)
            if self._use_mock and self._board.ping(1.0)[0]:'''
NEW_RE = '''            # 不再扫描其它串口（会抢走家居板的数据），只重试自己这个端口
            if self._use_mock and self._board.ping(1.2)[0]:'''
if OLD_RE in l:
    l = l.replace(OLD_RE, NEW_RE, 1)
    open(L, "w", encoding="utf-8").write(l)
    print("[lock] _reprobe 已改为只重试自己端口")
else:
    print("[lock] 状态:", "已改" if "只重试自己这个端口" in l else "未匹配")
