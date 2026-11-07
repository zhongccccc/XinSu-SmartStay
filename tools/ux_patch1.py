# -*- coding: utf-8 -*-
"""UI 优化：完成页信息强化、房卡跳过、呼叫前台。"""
P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

# 1) 房卡页加"跳过"按钮
s = s.replace('<button class="link" id="btnMockCard">演示：模拟放卡</button>',
'''<button class="link" id="btnMockCard">演示：模拟放卡</button>
          <button class="ghost skip-card" id="btnSkipCard">跳过，稍后在门锁上刷房卡绑定</button>''', 1)

# 2) 完成页：开门码放大 + 倒计时 + 绑定提示
s = s.replace('''          <div><span>临时开门码</span><b id="doneCode">------</b></div>''',
'''          <div><span>临时开门码</span><b id="doneCode" class="bigcode">------</b></div>''', 1)

s = s.replace('''        <div class="done-actions">''',
'''        <div class="done-hint">首次开门请先在门锁上刷这张房卡完成绑定</div>
        <div class="done-actions">''', 1)

s = s.replace('''          <button class="cta small" id="btnFinish">完成并返回</button>''',
'''          <button class="cta small" id="btnFinish">完成并返回<span class="cd" id="doneCd"></span></button>''', 1)

# 3) 待机页：呼叫前台浮动按钮
s = s.replace('    <!-- 语音服务面板 -->',
'''    <button class="call-staff" id="btnCallStaff">呼叫前台</button>

    <!-- 语音服务面板 -->''', 1)

open(P, "w", encoding="utf-8").write(s)
print("index.html 已更新")

# 4) CSS
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if '.bigcode' not in cs:
    cs += '''

/* 完成页强化 */
.done-info .bigcode{font-size:30px;letter-spacing:4px;color:#7fe3ff;font-weight:800}
.done-hint{font-size:12px;color:#8fa4c8;text-align:center;margin:6px 0 4px}
.done-actions .cd{font-size:12px;opacity:.75;margin-left:6px}

/* 房卡跳过 */
.skip-card{margin-top:14px;font-size:12px;padding:8px 16px;border-radius:10px}

/* 呼叫前台 */
.call-staff{position:absolute;right:18px;bottom:58px;z-index:30;
  padding:10px 18px;border-radius:12px;font-size:13px;cursor:pointer;
  background:linear-gradient(135deg,rgba(255,150,90,.9),rgba(255,90,110,.9));
  color:#2a0508;border:0;font-weight:700}
.call-staff:active{transform:scale(.96)}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("style.css 已更新")
