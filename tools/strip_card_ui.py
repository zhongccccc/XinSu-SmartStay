# -*- coding: utf-8 -*-
"""前端去掉"房卡"步骤。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD = "const STEP_ORDER = ['ident', 'face', 'room', 'pay', 'card', 'done'];"
NEW = "const STEP_ORDER = ['ident', 'face', 'room', 'pay', 'done'];"
if OLD in js:
    js = js.replace(OLD, NEW, 1)
    print("STEP_ORDER 已去掉房卡")
open(J, "w", encoding="utf-8").write(js)

H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()
OLDH = '''<i data-s="ident">身份</i><i data-s="face">人脸</i><i data-s="room">选房</i>
      <i data-s="pay">支付</i><i data-s="card">房卡</i><i data-s="done">完成</i>'''
NEWH = '''<i data-s="ident">身份</i><i data-s="face">人脸</i><i data-s="room">选房</i>
      <i data-s="pay">支付</i><i data-s="done">完成</i>'''
if OLDH in h:
    h = h.replace(OLDH, NEWH, 1)
    open(H, "w", encoding="utf-8").write(h)
    print("步骤条已去掉房卡")
else:
    print("步骤条未匹配")
