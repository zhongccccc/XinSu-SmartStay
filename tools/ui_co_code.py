# -*- coding: utf-8 -*-
"""无卡退房：改为输入开门码。"""
P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

s = s.replace('<button class="ghost" id="coGuidePick">没有房卡？选择房间</button>',
              '<button class="ghost" id="coGuidePick">没有房卡？输入开门码</button>', 1)

if 'id="coCode"' not in s:
    s = s.replace('    <!-- 退房：选择房间 -->',
'''    <!-- 无卡退房：输入开门码 -->
    <div class="exitmask" id="coCode">
      <div class="pinbox">
        <div class="pintitle">无卡退房 · 输入开门码</div>
        <div class="pindisp" id="coCodeDisp">— — — — — —</div>
        <div class="pinmsg" id="coCodeMsg">请输入入住时显示的 6 位开门码</div>
        <div class="pingrid">
          <button data-c="1">1</button><button data-c="2">2</button><button data-c="3">3</button>
          <button data-c="4">4</button><button data-c="5">5</button><button data-c="6">6</button>
          <button data-c="7">7</button><button data-c="8">8</button><button data-c="9">9</button>
          <button data-c="*">*</button><button data-c="0">0</button><button data-c="#">#</button>
        </div>
        <button class="ghost" id="coCodeClose">取消</button>
      </div>
    </div>

    <!-- 退房：选择房间 -->''', 1)
    print("index.html: 开门码弹层已加")

open(P, "w", encoding="utf-8").write(s)

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

if "bindCoCode" not in js:
    js += '''

/* 无卡退房：输入开门码 */
(function bindCoCode() {
  const mask = document.getElementById('coCode');
  const disp = document.getElementById('coCodeDisp');
  const msg = document.getElementById('coCodeMsg');
  const pick = document.getElementById('coGuidePick');
  const closeBtn = document.getElementById('coCodeClose');
  const guide = document.getElementById('coGuide');
  if (!mask || !pick) return;

  let buf = '';
  const render = () => {
    disp.textContent = buf.padEnd(6, '·').split('').join(' ');
  };

  const open = () => {
    buf = '';
    render();
    msg.textContent = '请输入入住时显示的 6 位开门码';
    mask.classList.add('on');
  };

  pick.onclick = () => {
    if (guide) guide.classList.remove('on');
    open();
  };
  if (closeBtn) closeBtn.onclick = () => mask.classList.remove('on');

  const submit = async () => {
    if (buf.length !== 6) { msg.textContent = '请输入完整的 6 位开门码'; return; }
    const r = await api('/api/checkout', { pin: buf });
    if (r && r.ok) {
      mask.classList.remove('on');
      const box = document.querySelector('#checkoutOk .co-ok-box');
      document.getElementById('coIcon').textContent = '✓';
      document.getElementById('coTitle').textContent = '退房成功';
      document.getElementById('coRoom').textContent = r.room || '';
      document.getElementById('coSub').textContent = '开门凭证已作废，欢迎再次光临';
      if (box) box.classList.remove('bad');
      const ok = document.getElementById('checkoutOk');
      if (ok) {
        ok.classList.add('on');
        clearTimeout(window.__coTimer);
        window.__coTimer = setTimeout(() => ok.classList.remove('on'), 6000);
      }
    } else {
      msg.textContent = (r && r.msg) || '开门码不正确';
      buf = '';
      render();
    }
  };

  mask.querySelectorAll('.pingrid button').forEach((b) => {
    b.onclick = () => {
      const k = b.dataset.c;
      if (k === '*') buf = buf.slice(0, -1);
      else if (k === '#') { submit(); return; }
      else if (buf.length < 6) buf += k;
      render();
    };
  });
})();
'''
    open(J, "w", encoding="utf-8").write(js)
    print("app.js: 开门码逻辑已加")
