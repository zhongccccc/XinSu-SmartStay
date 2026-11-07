# -*- coding: utf-8 -*-
"""把 /api/home 的 GET 路由放进 do_GET。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

GETROUTE = '''            if p == "/api/home":
                st = APP.home.status()
                g = (st.get("data") or {}).get("gas") or 0
                st["alarm"] = bool(g > 2500)
                return self._json(st)
'''
if 'if p == "/api/home":' not in s.split("def do_POST")[0]:
    anchor = '            if p.startswith("/photos/"):'
    s = s.replace(anchor, GETROUTE + anchor, 1)
    print("GET /api/home 已加")
else:
    print("GET 路由已存在")

open(P, "w", encoding="utf-8").write(s)
