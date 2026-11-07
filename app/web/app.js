/* 芯宿·智控 一体机前端 */
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));
let STATE = null;
let DEVICES = null;
let NET = { ip: '', ssid: '', host: 'shiqi.local' };
let LAST_STEP = null;
let IDLE_TIMER = null;

/* ---------- 自适应缩放：固定 800x480 舞台 ---------- */
function fit() {
  const s = Math.min(window.innerWidth / 800, window.innerHeight / 480);
  const st = $('#stage');
  st.style.transform = `translate(-50%,-50%) scale(${s})`;
}
window.addEventListener('resize', fit);

/* ---------- API ---------- */
async function api(path, body) {
  // body === null 表示 GET，其余一律 POST（默认空对象）
  if (body === null) {
    const r = await fetch(path);
    return await r.json();
  }
  const r = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  return await r.json();
}

/* ---------- 渲染 ---------- */
const STEP_ORDER = ['ident', 'face', 'room', 'pay', 'card', 'done'];
const MOCK = { id: {}, pay: {}, card: {} };

function showStep(step) {
  $$('.screen').forEach((el) => el.classList.remove('on'));
  const map = { idle: 'scr-idle', ident: 'scr-ident', face: 'scr-face', room: 'scr-room',
                pay: 'scr-pay', card: 'scr-card', issue: 'scr-issue', done: 'scr-done' };
  const el = document.getElementById(map[step] || 'scr-idle');
  if (el) el.classList.add('on');

  // 返回键：待机页没有上级；下发门锁是瞬态步骤，也不显示
  const back = $('#btnBack');
  if (back) back.classList.toggle('hide', step === 'idle' || step === 'issue');

  const idx = STEP_ORDER.indexOf(step);
  $$('#steps i').forEach((i) => {
    i.classList.remove('on', 'done');
    const k = STEP_ORDER.indexOf(i.dataset.s);
    if (k >= 0 && idx >= 0) {
      if (k < idx) i.classList.add('done');
      if (k === idx) i.classList.add('on');
    }
  });
}

function render(state) {
  if (!state) return;
  STATE = state;
  const step = state.step;
  showStep(step);
  if ($('#hotelSub')) $('#hotelSub').textContent = state.hotel_sub || '深圳湾科技园店';

  if (step === 'room') renderRooms(state);
  if (step === 'done' && window.__startDoneCountdown) window.__startDoneCountdown(120);
  const cs = document.querySelector('.call-staff');
  if (cs) cs.style.display = (step === 'idle') ? '' : 'none';
  if (step === 'pay') { $('#payAmount').textContent = state.price || 0; }
  if (step === 'done') {
    $('#doneRoom').textContent = (state.room && state.room.no) || '----';
    $('#doneCode').textContent = state.lock_code || '------';
    $('#doneCard').textContent = (STATE.card_uid && STATE.card_uid !== '-') ? STATE.card_uid : '未绑定';
    $('#doneLock').textContent = '已授权';
  }
  if (step === 'ident') {
    $('#identHint').textContent = state.msg || '芯片面朝上，平放于感应区，保持 6 秒';
  }
  if (step === 'face') {
    const img = $('#camImg');
    // 每次进入人脸页都重新拉流（避免上一次的连接错误留下黑屏）
    if (LAST_STEP !== 'face') {
      img.src = img.dataset.src + '?t=' + Date.now();
      if (window.__guardCam) window.__guardCam();
      /* 人脸：不自动通过，必须由用户点「立即识别」 */
      const bf = $('#btnFace');
      if (bf) { bf.disabled = false; bf.textContent = '立即识别'; }
    }
    img.style.display = 'block';
    $('#camFallback').style.display = state.camera_ok === false ? 'block' : 'none';
    const fh = $('#faceHint');
    if (fh) {
      if (state.face_reason && LAST_STEP !== 'face-in') {
        fh.textContent = state.face_reason;
        fh.style.color = '#ff9aa8';
      } else if (state.guest) {
        fh.textContent = `${state.guest} 您好，请保持面部在框内`;
        fh.style.color = '';
      }
    }
  } else if (LAST_STEP === 'face') {
    window.__autoFaceOnce = false;      /* 下次进人脸页重新自动放行 */
    const img = $('#camImg');
    img.removeAttribute('src');
    const bf = $('#btnFace');
    if (bf) { bf.disabled = false; bf.textContent = '立即识别'; }
  }
  LAST_STEP = step;
}

function renderRooms(state) {
  const g = $('#roomGrid');
  if (g.dataset.built === '1') return;
  g.dataset.built = '1';
  g.innerHTML = '';
  (state.rooms || []).forEach((r) => {
    const d = document.createElement('div');
    d.className = 'room' + (r.occupied ? ' room-busy' : '');
    d.innerHTML = `<b>${r.no}</b><div class="t">${r.type}</div>
      <div class="t">${(r.tags || []).map((t) => `<span class="tag">${t}</span>`).join('')}</div>
      <div class="p"><small>¥</small>${r.price}</div>` +
      (r.occupied ? '<div class="busy-badge">已订房</div>' : '');
    d.onclick = async () => {
      if (r.occupied) { toast('房间 ' + r.no + ' 已订房，请选择其他房间'); return; }
      await api('/api/room/' + r.no);
    };
    g.appendChild(d);
  });
}

function renderDevices(d) {
  if (!d) return;
  DEVICES = d;
  const bar = $('#devbar');
  bar.innerHTML = '';
  (d.items || []).forEach((it) => {
    const s = document.createElement('div');
    s.className = 'dev ' + (it.present ? 'ok' : 'off');
    s.innerHTML = `<i class="dot"></i>${it.label}`;
    s.title = it.detail || '';
    bar.appendChild(s);
  });
  const sp = document.createElement('div'); sp.className = 'spacer'; bar.appendChild(sp);
  const v = document.createElement('div'); v.className = 'ver';
  const isAdmin = document.body.classList.contains('admin');
  v.textContent = (isAdmin && NET.ip) ? ('K1 · ' + NET.ip) : 'RISC-V K1 · Bianbu 2.3.5';
  v.title = (NET.ssid ? ('WiFi: ' + NET.ssid + '   ') : '') + 'ssh shiqi@' + (NET.host || 'shiqi.local');
  bar.appendChild(v);
}

/* ---------- 事件 ---------- */
async function poll() {
  try {
    const st = await api('/api/state', null);
    render(st);
  } catch (e) { /* ignore */ }
  try {
    const dv = await api('/api/devices', null);
    renderDevices(dv);
  } catch (e) { /* ignore */ }
}

function connectSSE() {
  const es = new EventSource('/api/events');
  es.addEventListener('state', (e) => { try { render(JSON.parse(e.data).data); } catch (_) {} });
  es.addEventListener('scan', (e) => {
    let d = {};
    try { d = JSON.parse(e.data).data; } catch (_) {}
    flashScan(d.kind);
    toast('已识别 ' + (d.kind === 'rfid' ? '房卡 ' : '条码 ') + d.code);
    if (d.kind === 'rfid') { addMsg('（读到房卡 ' + d.code + '）', 'bot'); }
  });
  es.addEventListener('voice', (e) => {
    const d = JSON.parse(e.data).data;
    addMsgOnce(d.id, d.text, 'me');
    addMsgOnce(d.id, d.reply, 'bot');
    openSheet(true);
  });
  es.addEventListener('card_door', (e) => {
    let d = {};
    try { d = JSON.parse(e.data).data; } catch (_) {}
    const box = document.querySelector('#checkoutOk .co-ok-box');
    const mask = document.getElementById('checkoutOk');
    if (!mask) return;
    if (d && d.ok) {
      document.getElementById('coIcon').textContent = '✓';
      document.getElementById('coTitle').textContent = '退房成功';
      document.getElementById('coRoom').textContent = d.room || '';
      document.getElementById('coSub').textContent = '开门凭证已作废，欢迎再次光临';
      if (box) box.classList.remove('bad');
    } else {
      document.getElementById('coIcon').textContent = '!';
      document.getElementById('coTitle').textContent = '未找到入住记录';
      document.getElementById('coRoom').textContent = '';
      document.getElementById('coSub').textContent = '请确认房卡或到前台咨询';
      if (box) box.classList.add('bad');
    }
    mask.classList.add('on');
    clearTimeout(window.__coTimer);
    window.__coTimer = setTimeout(() => mask.classList.remove('on'), 6000);
  });  es.addEventListener('lock', (e) => {
    let d = {};
    try { d = JSON.parse(e.data).data; } catch (_) {}
    const t = (d.type || '').toUpperCase();
    if (t === 'DOOR') {
      toast(d.value === 'open' ? '门已打开' : '门已关闭');
    } else if (t === 'ALARM') {
      toast('门锁告警：' + d.value);
    } else if (t === 'CARD') {
      toast('门锁刷卡 ' + d.value);
    } else if (t === 'FP') {
      toast('指纹开门 #' + d.value);
    }
  });
  es.onerror = () => { es.close(); setTimeout(connectSSE, 3000); };
}

function flashScan(kind) {
  const el = $(kind === 'rfid' ? '#scr-card' : '#scr-pay');
  if (el) { el.animate([{ filter: 'brightness(1.6)' }, { filter: 'brightness(1)' }], 350); }
}

let TOAST_TIMER = null;
function toast(text) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = text;
  t.classList.add('on');
  if (TOAST_TIMER) clearTimeout(TOAST_TIMER);
  TOAST_TIMER = setTimeout(() => t.classList.remove('on'), 4000);
}

/* ---------- 交互 ---------- */
$('#btnStart').onclick = async () => { resetRoomGrid(); await api('/api/session/start'); };
$('#btnBack').onclick = async () => { await api('/api/back', {}); };
$('#btnMockId').onclick = () => api('/api/idcard/mock');
$('#btnMockPay').onclick = () => api('/api/pay', { code: 'MOCKPAY' + Date.now() });
$('#btnMockCard').onclick = () => api('/api/card', { uid: 'CARD' + Math.random().toString(16).slice(2, 8).toUpperCase() });
$('#btnFinish').onclick = async () => { resetRoomGrid(); await api('/api/reset'); };   /* 只回待机，保留门锁凭证 */
$('#btnFace').onclick = async () => {
  const b = $('#btnFace'); b.disabled = true; b.textContent = '识别中…';
  let done = false;
  const guard = setTimeout(() => {
    if (done) return;
    b.disabled = false; b.textContent = '开始人脸核验';
    toast('摄像头无响应，请重试或联系工作人员');
  }, 12000);
  try {
    await api('/api/face', { capture: true });
  } catch (_) {
    toast('网络异常，请重试');
  } finally {
    done = true; clearTimeout(guard);
    b.disabled = false; b.textContent = '开始人脸核验';
  }
  setTimeout(() => { b.disabled = false; b.textContent = '开始人脸核验'; }, 800);
};

function resetRoomGrid() { const g = $('#roomGrid'); g.dataset.built = '0'; }

/* ---------- 房卡跳过 ---------- */
(function bindSkipCard() {
  const b = document.getElementById('btnSkipCard');
  if (!b) return;
  b.onclick = async () => {
    b.disabled = true;
    await api('/api/card', { uid: '-' });   /* '-' = 待绑定，门锁首次刷卡时绑定 */
    b.disabled = false;
  };
})();

/* ---------- 呼叫前台 ---------- */
(function bindCallStaff() {
  const b = document.getElementById('btnCallStaff');
  if (!b) return;
  b.onclick = async () => {
    await api('/api/voice', { text: '呼叫前台，需要工作人员协助' });
    toast('已呼叫前台，请稍候');
  };
})();

/* ---------- 完成页开门码倒计时 ---------- */
(function bindDoneCountdown() {
  let timer = null;
  window.__startDoneCountdown = function (seconds) {
    const el = document.getElementById('doneCd');
    if (!el) return;
    clearInterval(timer);
    let left = seconds;
    const tick = () => {
      el.textContent = left > 0 ? '（' + left + 's）' : '';
      if (left-- <= 0) clearInterval(timer);
    };
    tick();
    timer = setInterval(tick, 1000);
  };
})();
/* ---------- 退房（待机页入口 + 房间列表） ---------- */
(function bindCheckout() {
  const sheet = () => $('#checkoutSheet');
  const listEl = () => $('#coList');

  function fill() {
    const rows = (STATE && STATE.inhouse) || [];
    const box = listEl();
    box.innerHTML = '';
    if (!rows.length) {
      box.innerHTML = '<div class="co-empty">当前没有在住订单</div>';
      return;
    }
    rows.slice(0, 20).forEach((o) => {
      const d = document.createElement('div');
      d.className = 'co-item';
      d.setAttribute('data-room', o.room || '');
      d.innerHTML = '<span>房间 <b>' + (o.room || '-') + '</b> · ' +
        (o.guest || '-') + ' · 码 ' + (o.lock_code || '-') + '</span><span>退房 ›</span>';
      box.appendChild(d);
    });
  }

  const btn = $('#btnCheckoutIdle');
  if (btn) window.__openCoSheet = () => { fill(); sheet().classList.add('on'); };

  const cl = $('#coClose');
  if (cl) cl.addEventListener('click', () => sheet().classList.remove('on'));

  const box = listEl();
  if (box) box.addEventListener('click', async (ev) => {
    const item = ev.target.closest ? ev.target.closest('.co-item') : null;
    if (!item) return;
    const room = item.getAttribute('data-room');
    if (!room) return;
    await api('/api/checkout', { room: room });
    toast('房间 ' + room + ' 已退房，凭证已作废');
    sheet().classList.remove('on');
  });
})();
/* ---------- 门锁键盘（板端本地校验） ---------- */
(function bindPinPad() {
  const mask = () => $('#pinPad');
  let buf = '';
  const disp = () => {
    const s = buf.padEnd(6, '—').split('').join(' ');
    $('#pinDisp').textContent = s;
  };
  const msg = (t, cls) => {
    const el = $('#pinMsg');
    el.textContent = t;
    el.className = 'pinmsg' + (cls ? ' ' + cls : '');
  };
  const co = $('#btnCheckout');
  if (co) {
    co.onclick = async () => {
      const r = await api('/api/checkout', {});
      toast((r && r.message) || '退房完成｜凭证已作废');
      resetRoomGrid();
    };
  }
  $('#btnDoorPad').onclick = () => {
    buf = '';
    disp();
    msg('输入开门码后按 #');
    mask().classList.add('on');
  };
  $('#btnPinClose').onclick = () => mask().classList.remove('on');
  document.querySelectorAll('#pinPad .pingrid button').forEach((b) => {
    b.onclick = async () => {
      const k = b.dataset.k;
      if (k === '*') { buf = ''; disp(); msg('已清空'); return; }
      if (k === '#') {
        if (buf.length < 4) { msg('至少 4 位', 'bad'); return; }
        msg('校验中…');
        const r = await api('/api/lock/code', { pin: buf });
        if (r.ok) { msg('✓ 门锁已开启（板端校验通过）', 'ok'); }
        else { msg('✗ 开门码错误（板端拒绝）', 'bad'); }
        buf = '';
        disp();
        return;
      }
      if (buf.length < 6) { buf += k; disp(); }
    };
  });
})();

/* ---------- 长按左上角 logo 1.5 秒 → 退出确认 ---------- */
(function bindExit() {
  const brand = document.querySelector('.brand');
  const mask = () => $('#exitMask');
  let timer = null;
  brand.addEventListener('pointerdown', () => {
    clearTimeout(timer);
    timer = setTimeout(() => mask().classList.add('on'), 1500);
  });
  ['pointerup', 'pointerleave', 'pointercancel'].forEach((ev) =>
    brand.addEventListener(ev, () => clearTimeout(timer)));
  $('#btnExitCancel').onclick = () => mask().classList.remove('on');
  $('#btnExitOk').onclick = async () => {
    mask().classList.remove('on');
    await api('/api/kiosk/exit', {});
  };
})();

/* 摄像头不可用降级 */
$('#camImg').onerror = () => {
  if (STATE && STATE.camera_ok) return;   // 有摄像头时可能是瞬时抖动，不隐藏画面
  $('#camImg').style.display = 'none';
  $('#camFallback').style.display = 'block';
};

/* ---------- 语音面板 ---------- */
function openSheet(on) { $('#serviceSheet').classList.toggle('on', on); }
$('#btnService').onclick = () => openSheet(!$('#serviceSheet').classList.contains('on'));
$('#btnCloseService').onclick = () => openSheet(false);

function addMsg(text, who) {
  const c = $('#chat');
  const d = document.createElement('div');
  d.className = 'msg ' + who;
  d.textContent = text;
  c.appendChild(d);
  c.scrollTop = c.scrollHeight;
}

/* 同一条语音消息会从 HTTP 响应和 SSE 推送各来一次，按 id 去重 */
const MSG_SEEN = new Set();
function addMsgOnce(id, text, who) {
  if (!text && text !== 0) return;
  if (!id) { addMsg(text, who); return; }
  const key = id + '|' + who;
  if (MSG_SEEN.has(key)) return;
  MSG_SEEN.add(key);
  if (MSG_SEEN.size > 300) MSG_SEEN.clear();
  addMsg(text, who);
}

async function sendVoice(text) {
  if (!text.trim()) return;
  const r = await api('/api/voice', { text });
  // 同一条消息会经 HTTP 和 SSE 各到一次，按 id 去重（谁先到谁渲染）
  addMsgOnce(r.id, r.text || text, 'me');
  addMsgOnce(r.id, r.reply || '（无应答）', 'bot');
}
$('#btnSend').onclick = () => { const v = $('#sayInput').value; $('#sayInput').value = ''; sendVoice(v); };
$('#sayInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') $('#btnSend').click(); });
$$('#quickCmds button').forEach((b) => { b.onclick = () => sendVoice(b.textContent); });

$('#btnMic').onclick = async () => {
  const b = $('#btnMic');
  b.classList.add('rec'); b.textContent = '🎙 录音中 4s…';
  await fetch('/api/voice', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: '' }) });
  setTimeout(() => { b.classList.remove('rec'); b.textContent = '🎙 说话'; }, 4000);
  addMsg('（麦克风已接入，端侧 ASR 待启用，可先用下方快捷指令或文字）', 'bot');
};

/* ---------- 时钟 ---------- */
function tick() {
  const d = new Date();
  $('#clock').textContent = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

/* ---------- 支付二维码（装饰用 canvas） ---------- */
function drawQr() {
  const c = $('#payQr'); if (!c) return;
  const ctx = c.getContext('2d');
  const n = 25, s = c.width / n;
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
  ctx.fillStyle = '#101a33';
  let seed = 7;
  const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    if (rnd() > 0.52) ctx.fillRect(x * s, y * s, s, s);
  }
  const corner = (ox, oy) => {
    ctx.fillStyle = '#101a33'; ctx.fillRect(ox, oy, s * 7, s * 7);
    ctx.fillStyle = '#fff'; ctx.fillRect(ox + s, oy + s, s * 5, s * 5);
    ctx.fillStyle = '#101a33'; ctx.fillRect(ox + s * 2, oy + s * 2, s * 3, s * 3);
  };
  corner(0, 0); corner(c.width - s * 7, 0); corner(0, c.height - s * 7);
}

/* ---------- 启动 ---------- */
fit(); tick(); setInterval(tick, 10000);
drawQr();
poll();
setInterval(poll, 3000);
connectSSE();

/* 诊断：上报视口与主按钮位置（排查触摸坐标） */
setTimeout(() => {
  try {
    const b = $('#btnStart').getBoundingClientRect();
    fetch('/api/debug/click', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ev: 'rect', x: Math.round(b.left), y: Math.round(b.top),
                             type: `${window.innerWidth}x${window.innerHeight}@${window.devicePixelRatio}`,
                             target: `${Math.round(b.width)}x${Math.round(b.height)}` })
    });
  } catch (_) {}
}, 1200);
document.addEventListener('pointerdown', (e) => {
  try {
    fetch('/api/debug/click', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: e.clientX, y: e.clientY, type: e.pointerType, ev: 'down',
                             target: (e.target && (e.target.id || e.target.className)) || '' })
    });
  } catch (_) {}
}, true);
document.addEventListener('click', (e) => {
  try {
    fetch('/api/debug/click', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: e.clientX, y: e.clientY, type: e.pointerType, ev: 'click',
                             target: (e.target && (e.target.id || e.target.className)) || '' })
    });
  } catch (_) {}
}, true);


/* 前台模式：URL 带 ?staff=1 才显示调试按钮 */
if (/[?&]staff=1/.test(location.search)) document.body.classList.add('staff');
if (/[?&]admin=1/.test(location.search)) {
  document.body.classList.add('staff');
  document.body.classList.add('admin');
}


/* 退房入口：明确引导 */
(function bindCoGuide() {
  const entry = document.getElementById('btnCheckoutIdle');
  const guide = document.getElementById('coGuide');
  const sheet = document.getElementById('checkoutSheet');
  if (!entry || !guide) return;
  /* 点「我要退房」时让后端播报怎么退房 */
  entry.addEventListener('click', () => {
    try { api('/api/checkout/guide', {}); } catch (_) {}
  });

  entry.onclick = () => guide.classList.add('on');
  const close = document.getElementById('coGuideClose');
  if (close) close.onclick = () => guide.classList.remove('on');
  const pick = document.getElementById('coGuidePick');
  if (pick) pick.onclick = () => {
    guide.classList.remove('on');
    if (window.__openCoSheet) window.__openCoSheet();
    else if (sheet) sheet.classList.add('on');
  };
  guide.onclick = (e) => { if (e.target === guide) guide.classList.remove('on'); };
})();

/* 调试：?co=1 直接打开退房引导 */
if (/[?&]co=1/.test(location.search)) {
  const g = document.getElementById('coGuide');
  if (g) setTimeout(() => g.classList.add('on'), 300);
}

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

/* 调试：?cocode=1 直接打开开门码键盘 */
if (/[?&]cocode=1/.test(location.search)) {
  setTimeout(() => {
    const p = document.getElementById('coGuidePick');
    if (p) p.click();
  }, 400);
}

/* 客房环境（智能家居板） */
(function bindHomeEnv() {
  const $id = (x) => document.getElementById(x);

  const paint = (d) => {
    if (!d) return;
    const data = d.data || {};
    const online = !!d.online;
    const dot = $id('envDot'), st = $id('envState');
    if (dot) dot.classList.toggle('on', online);
    if (st) st.textContent = online ? (d.firmware || '在线') : '未连接';

    const t = data.temp, h = data.hum, l = data.lux, g = data.gas;
    if ($id('envTemp')) $id('envTemp').textContent = (t == null || t < -90) ? '--' : t.toFixed(1);
    if ($id('envHum')) $id('envHum').textContent = (h == null || h < 0) ? '--' : h.toFixed(1);
    if ($id('envLux')) $id('envLux').textContent = (l == null || l < 0) ? '--' : l;
    if ($id('envGas')) $id('envGas').textContent = (g == null) ? '--' : g;
    if ($id('envPir')) $id('envPir').textContent = data.pir ? '有人' : '无人';
    if ($id('envPir')) $id('envPir').style.color = data.pir ? '#ff7a8a' : '#8fa4c8';
    if ($id('envLight')) {
      const lit = !!data.light;
      $id('envLight').textContent = lit ? '已开' : '已关';
      $id('envLight').style.color = lit ? '#ffc46b' : '#8fa4c8';
    }
    if ($id('envFan')) {
      const f = data.fan || 0;
      $id('envFan').textContent = f ? ('开 ' + f) : '开';
    }

    const chip = $id('envChip');
    if (chip) chip.textContent = ((t == null || t < -90) ? '--' : t.toFixed(1)) + '°C · ' +
      ((h == null || h < 0) ? '--' : h.toFixed(1)) + '%';

    const panel = $id('homeEnv');
    if (panel) panel.classList.toggle('alarm', !!(d.alarm || (g && g > 2500)));
    if ($id('envGas')) $id('envGas').style.color = (g && g > 2500) ? '#ff7a8a' : '#eaf2ff';
  };

  const refresh = async () => {
    try {
      const r = await fetch('/api/home');
      paint(await r.json());
    } catch (_) { }
  };

  const post = async (url, body) => {
    try { await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) }); } catch (_) { }
    refresh();
  };

  const on = (id, fn) => { const b = $id(id); if (b) b.onclick = fn; };
  on('btnEnvLightOn', () => { post('/api/home/light', { on: true }); toast('已开灯'); });
  on('btnEnvLightOff', () => { post('/api/home/light', { on: false }); toast('已关灯'); });
  on('btnEnvFanOn', () => { post('/api/home/fan', { duty: 60 }); toast('风扇已开'); });
  on('btnEnvFanOff', () => { post('/api/home/fan', { duty: 0 }); toast('风扇已关'); });

  setInterval(refresh, 5000);
  refresh();

  /* 燃气报警实时推送 */
  try {
    es.addEventListener('home_alarm', (e) => {
      let d = {};
      try { d = JSON.parse(e.data).data || {}; } catch (_) { }
      toast('⚠ 燃气浓度超标（' + (d.gas || '?') + '），已自动生成工单');
    });
    es.addEventListener('home_pir', (e) => {
      let d = {};
      try { d = JSON.parse(e.data).data || {}; } catch (_) { }
      if (d.pir) toast('客房检测到有人');
    });
  } catch (_) { }
})();

/* 调试：?svc=1 直接打开语音服务面板 */
if (/[?&]svc=1/.test(location.search)) {
  setTimeout(() => {
    const b = document.getElementById('btnService');
    if (b) b.click();
  }, 500);
}

/* 长按 logo 3 秒进入前台模式（现场无法输 URL 时用） */
(function bindStaffLongPress() {
  const logo = document.querySelector('.brand .logo');
  if (!logo) return;
  /* 长按 logo：只负责"退出应用"（管理员入口见下方 5 连点版本号） */
  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
    }, 3000);
  };
  const stop = () => clearTimeout(t);
  logo.addEventListener('mousedown', start);
  logo.addEventListener('touchstart', start, { passive: true });
  logo.addEventListener('mouseup', stop);
  logo.addEventListener('mouseleave', stop);
  logo.addEventListener('touchend', stop);
})();


/* 摄像头流保护：4 秒内没出画就切到降级提示，并停止重试，避免渲染进程空转 */
(function guardCamStream() {
  const img = document.getElementById('camImg');
  const fb = document.getElementById('camFallback');
  if (!img) return;
  let tries = 0;

  const showFallback = (msg) => {
    img.style.display = 'none';
    if (fb) { fb.style.display = 'flex'; fb.textContent = msg || '摄像头暂时不可用'; }
  };

  img.addEventListener('load', () => {
    tries = 0;
    clearTimeout(window.__camTimer);
    img.style.display = '';
    if (fb) fb.style.display = 'none';
  });

  img.addEventListener('error', () => {
    tries += 1;
    if (tries >= 2) { showFallback('摄像头暂时不可用，请联系工作人员'); return; }
    setTimeout(() => { img.src = img.dataset.src + '?t=' + Date.now(); }, 1500);
  });

  window.__guardCam = () => {
    clearTimeout(window.__camTimer);
    window.__camTimer = setTimeout(() => {
      if (!img.complete || img.naturalWidth === 0) {
        showFallback('摄像头画面加载超时');
        img.removeAttribute('src');   /* 断开流，防止无限重连 */
      }
    }, 4000);
  };
})();


/* ---------- 管理员模式：任意房间退房 ---------- */
(function bindAdminMode() {
  const $id = (x) => document.getElementById(x);

  /* 退出管理员模式 */
  const badge = $id('adminBadge');
  if (badge) badge.onclick = () => {
    document.body.classList.remove('admin');
    document.body.classList.remove('staff');
    if (typeof renderDevices === 'function') renderDevices(DEVICES);
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


/* 调试：?cosheet=1 自动打开退房列表 */
if (/[?&]cosheet=1/.test(location.search)) {
  setTimeout(() => {
    if (window.__openCoSheet) window.__openCoSheet();
  }, 1500);
}


/* ---------- 管理员入口：连点右下角版本号 5 次 ---------- */
(function bindAdminGesture() {
  let taps = 0;
  let timer = null;

  document.addEventListener('click', (ev) => {
    const t = ev.target;
    if (!t || !t.classList || !t.classList.contains('ver')) return;
    taps += 1;
    clearTimeout(timer);
    timer = setTimeout(() => { taps = 0; }, 2500);
    if (taps >= 5) {
      taps = 0;
      document.body.classList.add('staff');
      document.body.classList.add('admin');
      if (typeof renderDevices === 'function') renderDevices(DEVICES);
      try { toast('已进入管理员模式'); } catch (_) {}
    }
  });
})();


/* ---------- 底部显示当前 IP ---------- */
(function showNet() {
  const paint = (d) => {
    if (!d) return;
    NET = { ip: d.ip || '', ssid: d.ssid || '', host: d.host || 'shiqi.local' };
    renderDevices(DEVICES);      /* 重建 devbar，带上 IP */
  };
  const load = async () => {
    try {
      const r = await fetch('/api/net');
      paint(await r.json());
    } catch (_) {}
  };
  load();
  setInterval(load, 60000);
})();


/* ---------- 人脸：点「立即识别」→ 5 秒后进入下一步 ---------- */
(function bindFaceCapture() {
  const btn = document.getElementById('btnFace');
  if (!btn) return;
  if (btn.dataset.bound === '1') return;
  btn.dataset.bound = '1';

  btn.addEventListener('click', async () => {
    if (btn.disabled) return;
    if (!STATE || STATE.step !== 'face') return;

    btn.disabled = true;
    const hint = document.getElementById('faceHint');
    const old = hint ? hint.textContent : '';
    /* 立刻发起比对（本机模型约 3~5 秒），期间显示进度 */
    if (hint) { hint.textContent = '正在比对… 请保持不动'; hint.style.color = ''; }

    const doVerify = async () => {
      let res = null;
      try {
        res = await api('/api/face', { capture: true });
      } catch (_) {}
      const st = res || STATE || {};
      if (st.step && st.step !== 'face') return;      /* 通过，页面会切走 */
      /* 没通过：恢复按钮并说明原因 */
      btn.disabled = false;
      btn.textContent = '重新识别';
      const f = (st.face) || {};
      const why = f.reason || st.face_reason || '未通过，请正对摄像头再试一次';
      const sc = (typeof f.score === 'number') ? `（相似度 ${f.score.toFixed(2)}）` : '';
      if (hint) {
        hint.textContent = why + sc;
        hint.style.color = '#ff9aa8';
      }
    };

    doVerify();
  });
})();


/* ---------- 人脸页：跳过人脸（测试用，事件委托） ---------- */
(function bindFaceSkip() {
  let busy = false;
  document.addEventListener('click', async (ev) => {
    const t = ev.target;
    const btn = (t && t.closest) ? t.closest('#btnFaceSkip') : null;
    if (!btn || busy) return;
    ev.preventDefault();
    ev.stopPropagation();
    if (!STATE || STATE.step !== 'face') {
      try { toast('当前不在人脸页'); } catch (_) {}
      return;
    }
    busy = true;
    btn.disabled = true;
    const hint = document.getElementById('faceHint');
    if (hint) { hint.textContent = '测试模式：正在跳过…'; hint.style.color = '#ffd28a'; }
    try { toast('已跳过人脸比对'); } catch (_) {}
    try {
      const r = await api('/api/face', { skip: true });
      if (!r || !r.step) throw new Error('no response');
    } catch (e) {
      busy = false;
      btn.disabled = false;
      if (hint) hint.textContent = '跳过失败，请重试';
    }
  }, true);
})();
