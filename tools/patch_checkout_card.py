# -*- coding: utf-8 -*-
"""把待机刷卡改为"刷卡退房"。"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

start = s.index("    def _card_unlock(self, uid):")
end = s.index("    def _auto_issue(self):")

NEW = '''    def _card_unlock(self, uid):
        """大堂一体机刷房卡：

        - 卡号匹配到在住订单 → **办退房**（作废门锁凭证 + 关单）
        - 匹配不到 → 提示未找到入住记录
        """
        uid = (uid or "").strip().upper()
        order = None
        for o in self.db.inhouse_orders():
            if (o["card_uid"] or "").strip().upper() == uid:
                order = o
                break

        if not order:
            self.last_card = {"ok": False, "mode": "checkout", "uid": uid,
                              "room": None, "reason": "no-order"}
            self.db.audit("checkout_denied", dict(self.last_card))
            return self.snapshot()

        room = order["room"]
        ok, detail = False, ""
        try:
            ok, detail = self.lock.revoke(room)
        except Exception as e:
            detail = str(e)
        try:
            self.db.checkout(order["id"])
        except Exception as e:
            self.db.audit("error", {"where": "checkout", "err": str(e)})

        self.last_card = {"ok": ok, "mode": "checkout", "uid": uid,
                          "room": room, "reason": str(detail)[:40]}
        self.db.audit("lock_checkout", dict(self.last_card))
        self._say("房间%s退房成功，开门凭证已作废" % room)
        return self.snapshot()

'''
s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
print("model.py: 刷卡退房已实现")
