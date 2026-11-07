#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把遗留的测试在住订单全部置为已退房。"""
import glob
import sqlite3
import time

paths = (glob.glob('/opt/zhikong/data/*.db') + glob.glob('/opt/zhikong/*.db')
         + glob.glob('/opt/zhikong/app/data/*.db'))
print("数据库:", paths)
for p in paths:
    try:
        c = sqlite3.connect(p)
        n = c.execute("SELECT COUNT(*) FROM orders WHERE status='inhouse'").fetchone()[0]
        c.execute("UPDATE orders SET status='checkedout', checkout_at=? WHERE status='inhouse'",
                  (time.time(),))
        c.commit()
        c.close()
        print("  %s: 清理 %d 条" % (p, n))
    except Exception as e:
        print("  %s: %s" % (p, e))
