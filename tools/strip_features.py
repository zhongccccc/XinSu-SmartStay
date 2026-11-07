# -*- coding: utf-8 -*-
"""按用户要求精简：
1. 去掉"支付后必须刷房卡"这一步 —— 直接下发凭证
2. 去掉入住/退房的房间联动（迎宾/节能模式）
"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

# ---- 1) 支付后直接进下发，不经过房卡 ----
OLD_PAY = '''        self._say("支付成功，请将房卡放在读卡区为您写卡")
        return self._goto("card", "支付成功，请将房卡放在读卡区", card_uid=None)'''
NEW_PAY = '''        self._say("支付成功，正在下发门锁凭证")
        # 不再单独刷房卡：凭证直接下发，房卡可在门锁上首刷绑定
        self.state["card_uid"] = "-"
        snap = self._goto("issue", "支付成功，正在下发门锁凭证", card_uid="-")
        threading.Thread(target=self._auto_issue, daemon=True, name="auto-issue").start()
        return snap'''
if OLD_PAY in s:
    s = s.replace(OLD_PAY, NEW_PAY, 1)
    print("已去掉房卡步骤")

# ---- 2) 去掉房间联动 ----
OLD_WELCOME = '''            threading.Thread(target=self.apply_room_mode, args=("welcome", st["room"]["no"]),
                             daemon=True, name="room-welcome").start()'''
if OLD_WELCOME in s:
    s = s.replace(OLD_WELCOME, "            pass", 1)
    print("已去掉入住迎宾模式")

OLD_ECO = '''        # 房间节能复位：灯、风扇全关
        self.apply_room_mode("eco", room)
'''
if OLD_ECO in s:
    s = s.replace(OLD_ECO, "", 1)
    print("已去掉退房节能模式")

open(P, "w", encoding="utf-8").write(s)
