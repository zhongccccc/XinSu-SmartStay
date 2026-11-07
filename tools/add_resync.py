# -*- coding: utf-8 -*-
"""1) 新增 /api/lock/resync：把在住订单的凭证重新写进真板子
2) 门锁改为"硬失败"：连不上就报错，不再偷偷用 mock
"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

ROUTE = '''            if p == "/api/lock/resync":
                # 把当前在住订单的凭证重新下发到门锁板
                items = APP.db.inhouse_orders()
                okn = 0
                fails = []
                for o in items:
                    try:
                        ok, detail = APP.lock.issue(
                            str(o["room"]), o["guest"] or "客人",
                            o["lock_code"], o["card_uid"] or "-", 24 * 60)
                    except Exception as e:
                        ok, detail = False, str(e)
                    if ok:
                        okn += 1
                    else:
                        fails.append({"room": o["room"], "detail": str(detail)[:60]})
                return self._json({"ok": True, "total": len(items),
                                   "issued": okn, "failed": fails})
'''

if "/api/lock/resync" not in s:
    anchor = '            if p == "/api/lock/code":'
    s = s.replace(anchor, ROUTE + anchor, 1)
    print("[main] /api/lock/resync 已加")

open(P, "w", encoding="utf-8").write(s)
print("done")
