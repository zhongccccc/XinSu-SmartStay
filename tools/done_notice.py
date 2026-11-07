# -*- coding: utf-8 -*-
"""完成页：在临时开门码旁边加"请拍照留存、勿外传"的醒目提醒。"""
H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()

OLD = '''        <div class="done-hint" id="cardBind">开门码可在门锁键盘上输入；若已领房卡，首次刷卡即完成绑定</div>'''

NEW = '''        <div class="done-warn">
          <div class="dw-title">请立即拍照留存</div>
          <div class="dw-text">开门码仅在本页显示，返回后不再提供查询。<br>
            请勿告知他人、勿发到群聊或网络，谨防他人冒用。</div>
        </div>
        <div class="done-hint" id="cardBind">开门码可在门锁键盘上输入；若已领房卡，首次刷卡即完成绑定</div>'''

if "done-warn" not in h and OLD in h:
    h = h.replace(OLD, NEW, 1)
    open(H, "w", encoding="utf-8").write(h)
    print("[html] 提醒已加")
else:
    print("[html] 状态:", "已存在" if "done-warn" in h else "未匹配")

C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if ".done-warn" not in cs:
    cs += '''

/* ---------- 完成页：拍照留存提醒 ---------- */
.done-warn{
  width:100%;max-width:520px;margin:10px auto 6px;padding:10px 16px;
  border-radius:12px;text-align:center;
  background:linear-gradient(180deg,rgba(255,179,71,.16),rgba(255,179,71,.07));
  border:1px solid rgba(255,179,71,.55);
}
.done-warn .dw-title{
  font-size:16px;font-weight:800;color:#ffce7a;letter-spacing:1px;margin-bottom:3px;
}
.done-warn .dw-title::before{content:"⚠  ";}
.done-warn .dw-text{font-size:12px;line-height:1.6;color:#f0d9b5}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("[css] 样式已加")
else:
    print("[css] 已存在")
