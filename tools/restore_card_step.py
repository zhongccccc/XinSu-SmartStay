# -*- coding: utf-8 -*-
"""恢复"支付后刷房卡"这一步（用户要求）。"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

NEW = '''        self._say("支付成功，请将房卡放在读卡区为您写卡")
        return self._goto("card", "支付成功，请将房卡放在读卡区", card_uid=None)'''

OLD = '''        self._say("支付成功，正在下发门锁凭证")
        # 不再单独刷房卡：凭证直接下发，房卡可在门锁上首刷绑定
        self.state["card_uid"] = "-"
        snap = self._goto("issue", "支付成功，正在下发门锁凭证", card_uid="-")
        threading.Thread(target=self._auto_issue, daemon=True, name="auto-issue").start()
        return snap'''

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("房卡步骤已恢复（后端）")
open(P, "w", encoding="utf-8").write(s)

# 前端：步骤条与顺序恢复
H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()
if 'data-s="card"' not in h:
    h = h.replace('<i data-s="pay">支付</i><i data-s="done">完成</i>',
                  '<i data-s="pay">支付</i><i data-s="card">房卡</i><i data-s="done">完成</i>', 1)
    open(H, "w", encoding="utf-8").write(h)
    print("步骤条已恢复房卡")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
if "'card'" not in js.split("STEP_ORDER")[1][:120]:
    js = js.replace("const STEP_ORDER = ['ident', 'face', 'room', 'pay', 'done'];",
                    "const STEP_ORDER = ['ident', 'face', 'room', 'pay', 'card', 'done'];", 1)
    open(J, "w", encoding="utf-8").write(js)
    print("STEP_ORDER 已恢复房卡")
