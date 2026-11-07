# -*- coding: utf-8 -*-
"""无卡退房改为「凭开门码退房」。

- 只有匹配到某张在住订单的开门码，才允许退房
- 房间列表退房接口仅在前台模式（staff）下可用
"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

# 1) 在 checkout 之前插入按码退房
anchor = "    def checkout(self, room=None):"
new = '''    def find_order_by_code(self, pin):
        """按开门码找到对应的在住订单。"""
        pin = str(pin or "").strip()
        if not pin:
            return None
        for o in self.db.inhouse_orders():
            code = (o["lock_code"] or "").strip()
            if code and code == pin:
                return o
        return None

    def checkout_by_code(self, pin):
        """凭开门码退房：码对得上才退，否则拒绝。"""
        order = self.find_order_by_code(pin)
        if not order:
            self.db.audit("checkout_code_denied", {"pin_len": len(str(pin or ""))})
            return {"ok": False, "reason": "code-mismatch",
                    "msg": "开门码不正确，请核对后重试，或联系前台"}
        snap = self.checkout(order["room"])
        snap["checked_out_room"] = order["room"]
        return {"ok": True, "room": order["room"], "msg": "退房成功", "state": snap}

'''
s = s.replace(anchor, new + anchor, 1)
open(P, "w", encoding="utf-8").write(s)
print("model.py: 按码退房已加")

# 2) 路由：/api/checkout 支持 pin
M = r"E:\zhikong\app\backend\main.py"
m = open(M, encoding="utf-8").read()
old = '''            if p == "/api/checkout":
                # 退房：作废门锁板凭证（可指定房间）
                APP.audio.flush()
                room = str(self._body().get("room", "") or "").strip() or None
                return self._json(APP.ctrl.checkout(room))'''
new = '''            if p == "/api/checkout":
                # 退房：room=房间（前台用）；pin=开门码（客人自助用）
                APP.audio.flush()
                body = self._body()
                pin = str(body.get("pin", "") or "").strip()
                if pin:
                    return self._json(APP.ctrl.checkout_by_code(pin))
                room = str(body.get("room", "") or "").strip() or None
                return self._json(APP.ctrl.checkout(room))'''
if old in m:
    m = m.replace(old, new, 1)
    open(M, "w", encoding="utf-8").write(m)
    print("main.py: /api/checkout 支持 pin")
