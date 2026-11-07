# -*- coding: utf-8 -*-
"""完成页清理：去掉"已开启灯光与通风"和房卡相关过时文案。"""
H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()

h = h.replace('        <div class="done-hint" id="roomReady">房间已为您开启灯光与通风</div>\n', '')
h = h.replace('<div class="done-hint" id="cardBind">首次开门请先在门锁上刷这张房卡完成绑定</div>',
              '<div class="done-hint" id="cardBind">开门码可在门锁键盘上输入；若已领房卡，首次刷卡即完成绑定</div>')
open(H, "w", encoding="utf-8").write(h)
print("完成页文案已清理")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
import re
m = re.search(r"\$\('#doneCard'\)\.textContent\s*=\s*([^;]+);", js)
if m:
    old = m.group(0)
    new = ("$('#doneCard').textContent = (STATE.card_uid && STATE.card_uid !== '-') "
           "? STATE.card_uid : '未绑定';")
    js = js.replace(old, new, 1)
    open(J, "w", encoding="utf-8").write(js)
    print("房卡字段已处理:", old.strip()[:60])
else:
    print("未找到 doneCard 赋值语句")
