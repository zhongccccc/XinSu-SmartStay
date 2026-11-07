# -*- coding: utf-8 -*-
"""管理员模式：长按 logo 进入，可对任意在住房间强制退房。"""
import re

# ---------------- HTML ----------------
H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()

if 'id="btnAdminCheckout"' not in h:
    # 管理员悬浮按钮 + 标记
    h = h.replace('    <button class="call-staff" id="btnCallStaff">呼叫前台</button>',
'''    <!-- 管理员模式 -->
    <div class="admin-badge" id="adminBadge">管理员模式 · 点此退出</div>
    <button class="admin-btn" id="btnAdminCheckout">退房管理</button>

    <button class="call-staff" id="btnCallStaff">呼叫前台</button>''', 1)

    # 退房确认弹层
    h = h.replace('    <!-- 退房：选择房间 -->',
'''    <!-- 管理员：退房确认 -->
    <div class="exitmask" id="coConfirm">
      <div class="pinbox co-box">
        <div class="pintitle">确认退房</div>
        <div class="co-confirm-txt" id="coConfirmTxt">确定要为该房间退房吗？</div>
        <div class="co-confirm-sub">退房后开门码与房卡立即失效</div>
        <div class="guide-actions">
          <button class="ghost" id="coCancelBtn">取消</button>
          <button class="cta small" id="coOkBtn">确认退房</button>
        </div>
      </div>
    </div>

    <!-- 退房：选择房间 -->''', 1)
    print("HTML 已加管理员元素")

open(H, "w", encoding="utf-8").write(h)

# ---------------- CSS ----------------
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if ".admin-btn" not in cs:
    cs += '''

/* ---------- 管理员模式 ---------- */
.admin-btn, .admin-badge{display:none}
body.admin .admin-btn{
  display:block;position:absolute;right:16px;bottom:96px;z-index:40;
  padding:12px 20px;border-radius:12px;font-size:14px;font-weight:700;cursor:pointer;
  background:linear-gradient(135deg,#ff9a5a,#ff5a6e);color:#2a0508;border:0;
  box-shadow:0 6px 18px rgba(255,90,110,.35)}
body.admin .admin-btn:active{transform:scale(.96)}
body.admin .admin-badge{
  display:block;position:absolute;left:50%;top:8px;transform:translateX(-50%);
  z-index:45;padding:6px 16px;border-radius:999px;font-size:12px;cursor:pointer;
  background:rgba(255,90,110,.16);border:1px solid rgba(255,90,110,.6);color:#ff9aa8}
.co-confirm-txt{font-size:17px;color:#eaf2ff;text-align:center;margin:14px 0 6px}
.co-confirm-sub{font-size:12px;color:#8fa4c8;text-align:center;margin-bottom:16px}
.co-item{cursor:pointer}
.co-item:active{background:rgba(255,255,255,.06)}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("CSS 已加")

# ---------------- JS ----------------
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

# 1) 长按逻辑改成：4 秒 → 同时进入 staff + admin
OLD_PRESS = """  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
      try { toast('已进入前台模式'); } catch (_) {}
    }, 3000);
  };"""
NEW_PRESS = """  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
      document.body.classList.add('admin');
      try { toast('已进入管理员模式'); } catch (_) {}
    }, 4000);
  };"""
if OLD_PRESS in js:
    js = js.replace(OLD_PRESS, NEW_PRESS, 1)
    print("长按已改为 4 秒进管理员模式")

# 2) 管理员退房逻辑
if "bindAdminMode" not in js:
    js += '''

/* ---------- 管理员模式：任意房间退房 ---------- */
(function bindAdminMode() {
  const $id = (x) => document.getElementById(x);

  /* 退出管理员模式 */
  const badge = $id('adminBadge');
  if (badge) badge.onclick = () => {
    document.body.classList.remove('admin');
    document.body.classList.remove('staff');
    const s = $id('checkoutSheet'); if (s) s.classList.remove('on');
    const c = $id('coConfirm'); if (c) c.classList.remove('on');
    try { toast('已退出管理员模式'); } catch (_) {}
  };

  /* 打开退房管理 */
  const btn = $id('btnAdminCheckout');
  if (btn) btn.onclick = () => {
    if (window.__openCoSheet) window.__openCoSheet();
  };

  /* 点房间 -> 先确认，再退房 */
  let pendingRoom = null;
  const list = $id('coList');
  if (list) {
    list.addEventListener('click', (ev) => {
      const item = ev.target.closest ? ev.target.closest('.co-item') : null;
      if (!item) return;
      /* 只接管管理员模式下的点击；普通模式保持原逻辑 */
      if (!document.body.classList.contains('admin')) return;
      ev.stopPropagation();
      ev.preventDefault();
      pendingRoom = item.getAttribute('data-room') || null;
      if (!pendingRoom) return;
      const txt = $id('coConfirmTxt');
      if (txt) txt.textContent = '确定为房间 ' + pendingRoom + ' 退房吗？';
      const s = $id('checkoutSheet'); if (s) s.classList.remove('on');
      const c = $id('coConfirm'); if (c) c.classList.add('on');
    }, true);   /* 捕获阶段先处理，避免和原逻辑冲突 */
  }

  const cancel = $id('coCancelBtn');
  if (cancel) cancel.onclick = () => {
    const c = $id('coConfirm'); if (c) c.classList.remove('on');
    const s = $id('checkoutSheet'); if (s) s.classList.add('on');
  };

  const ok = $id('coOkBtn');
  if (ok) ok.onclick = async () => {
    const c = $id('coConfirm'); if (c) c.classList.remove('on');
    if (!pendingRoom) return;
    const room = pendingRoom;
    pendingRoom = null;
    try {
      const r = await api('/api/checkout', { room: room });
      if (r && r.ok === false) {
        toast('房间 ' + room + ' 退房失败，请重试');
      } else {
        toast('房间 ' + room + ' 已退房，凭证已作废');
      }
    } catch (_) {
      toast('网络异常，退房失败');
    }
  };
})();
'''
    print("JS 已加管理员退房逻辑")

open(J, "w", encoding="utf-8").write(js)
print("完成")
