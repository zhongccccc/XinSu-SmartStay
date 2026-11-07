#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查历史刷卡记录 + 当前读卡器状态。"""
import sqlite3

c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
rows = list(c.execute("SELECT ts, payload FROM audit WHERE kind='scan' ORDER BY id DESC LIMIT 12"))
print("=== 历史 scan 记录（最近 12 条）===")
if not rows:
    print("  （没有任何刷卡记录）")
for ts, payload in rows:
    print("  ", payload)
c.close()
