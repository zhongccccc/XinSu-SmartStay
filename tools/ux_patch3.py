# -*- coding: utf-8 -*-
"""给退房一个明确入口：待机页按钮 + 刷卡引导页。"""
P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

# 1) 待机页：把主按钮文案改清楚，并加显眼的「退房」入口
s = s.replace('<button class="cta" id="btnStart"><span>触摸屏幕开始入住</span><em>退房请直接刷房卡</em></button>',
              '<button class="cta" id="btnStart"><span>触摸屏幕开始入住</span><em>请准备好二代身份证</em></button>', 1)

s = s.replace('        <!-- 退房改为刷房卡，按钮保留但隐藏（前台应急可用 API） -->',
'''        <button class="ghost co-entry" id="btnCheckoutIdle">我要退房</button>''', 1)

# 2) 退房引导弹层
s = s.replace('    <!-- 退房：选择房间 -->',
'''    <!-- 退房引导：请刷卡 -->
    <div class="exitmask" id="coGuide">
      <div class="pinbox co-guide">
        <div class="pintitle">办理退房</div>
        <div class="guide-card"><div class="guide-card-icon">▣</div><div class="guide-card-wave"></div></div>
        <div class="guide-main">请将房卡放在读卡区</div>
        <div class="guide-sub">系统会自动识别您的房间并作废开门凭证</div>
        <div class="guide-actions">
          <button class="ghost" id="coGuidePick">没有房卡？选择房间</button>
          <button class="ghost" id="coGuideClose">取消</button>
        </div>
      </div>
    </div>

    <!-- 退房：选择房间 -->''', 1)

open(P, "w", encoding="utf-8").write(s)
print("index.html ok")

C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if ".co-entry" not in cs:
    cs += '''

/* 退房入口 */
.co-entry{margin-top:14px;font-size:14px;padding:12px 30px;border-radius:14px;
  border:1px solid rgba(127,212,255,.45);color:#9fe0ff;background:rgba(20,40,70,.55);
  cursor:pointer;letter-spacing:2px}
.co-entry:active{transform:scale(.97)}

/* 退房引导 */
.co-guide{text-align:center;min-width:360px}
.guide-card{position:relative;width:110px;height:70px;margin:14px auto 10px;
  border-radius:10px;background:linear-gradient(135deg,#1b3c5e,#0e2033);
  border:1px solid rgba(127,212,255,.5);display:flex;align-items:center;justify-content:center}
.guide-card-icon{font-size:30px;color:#7fd4ff}
.guide-card-wave{position:absolute;inset:-6px;border-radius:14px;
  border:2px solid rgba(127,212,255,.35);animation:wv 1.6s ease-out infinite}
@keyframes wv{0%{opacity:.9;transform:scale(.94)}100%{opacity:0;transform:scale(1.12)}}
.guide-main{font-size:20px;color:#eaf2ff;margin-top:6px;letter-spacing:1px}
.guide-sub{font-size:12px;color:#8fa4c8;margin-top:6px}
.guide-actions{margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.guide-actions .ghost{font-size:12px;padding:8px 14px;border-radius:10px}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("style.css ok")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
if "coGuide" not in js:
    js += '''

/* 退房入口：明确引导 */
(function bindCoGuide() {
  const entry = document.getElementById('btnCheckoutIdle');
  const guide = document.getElementById('coGuide');
  const sheet = document.getElementById('checkoutSheet');
  if (!entry || !guide) return;

  entry.onclick = () => guide.classList.add('on');
  const close = document.getElementById('coGuideClose');
  if (close) close.onclick = () => guide.classList.remove('on');
  const pick = document.getElementById('coGuidePick');
  if (pick) pick.onclick = () => {
    guide.classList.remove('on');
    if (sheet) sheet.classList.add('on');
  };
  guide.onclick = (e) => { if (e.target === guide) guide.classList.remove('on'); };
})();
'''
    open(J, "w", encoding="utf-8").write(js)
    print("app.js ok")
