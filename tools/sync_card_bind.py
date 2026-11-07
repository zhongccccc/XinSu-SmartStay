# -*- coding: utf-8 -*-
"""门锁板首刷卡绑定时，把卡号同步回订单（这样退房刷卡能匹配到）。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''        if kind == "DOOR":
            log("[lock] 门磁：%s" % value)'''
NEW = '''        if kind == "CARDBIND":
            # 形如 "8805|0AD21E00"：客人在门锁板首刷，把卡号记到该房间订单上
            try:
                room, uid = (value or "").split("|", 1)
                room, uid = room.strip(), uid.strip().upper()
                n = 0
                for o in self.db.inhouse_orders():
                    if str(o["room"]) == room:
                        self.db.set_order_card(o["id"], uid)
                        n += 1
                        break
                log("[lock] 房卡绑定同步: 房间 %s <- 卡 %s (%d)" % (room, uid, n))
                BUS.publish("card_bound", {"room": room, "uid": uid})
            except Exception as e:
                log("[lock] CARDBIND 处理失败: %s (value=%r)" % (e, value))
        elif kind == "DOOR":
            log("[lock] 门磁：%s" % value)'''

if "CARDBIND" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[main] CARDBIND 同步已加")
else:
    print("状态:", "已存在" if "CARDBIND" in s else "未匹配")

# db: 增加 set_order_card
D = r"E:\zhikong\app\backend\core\db.py"
db = open(D, encoding="utf-8").read()
if "def set_order_card" not in db:
    anchor = "    def inhouse_orders(self"
    helper = '''    def set_order_card(self, order_id, uid):
        """把卡号写到订单上（门锁板首刷绑定时用）。"""
        cur = self._conn.cursor()
        cur.execute("UPDATE orders SET card_uid=? WHERE id=?", (uid, order_id))
        self._conn.commit()

'''
    if anchor in db:
        db = db.replace(anchor, helper + anchor, 1)
        open(D, "w", encoding="utf-8").write(db)
        print("[db] set_order_card 已加")
    else:
        print("[db] 未匹配")
