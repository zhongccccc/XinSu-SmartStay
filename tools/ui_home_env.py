# -*- coding: utf-8 -*-
"""一体机加「客房环境」面板：显示家居板数据 + 灯/风扇控制。"""
P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

if 'id="homeEnv"' not in s:
    s = s.replace('''      <div class="chat" id="chat"></div>''',
'''      <!-- 客房环境（来自智能家居板） -->
      <div class="env-panel" id="homeEnv">
        <div class="env-head">
          <b>客房环境</b>
          <span class="env-dot" id="envDot"></span>
          <span class="env-state" id="envState">连接中…</span>
        </div>
        <div class="env-grid">
          <div class="env-cell"><span>温度</span><b id="envTemp">--</b><i>°C</i></div>
          <div class="env-cell"><span>湿度</span><b id="envHum">--</b><i>%</i></div>
          <div class="env-cell"><span>光照</span><b id="envLux">--</b><i>lx</i></div>
          <div class="env-cell"><span>燃气</span><b id="envGas">--</b><i></i></div>
          <div class="env-cell"><span>人体</span><b id="envPir">--</b><i></i></div>
          <div class="env-cell"><span>灯光</span><b id="envLight">--</b><i></i></div>
        </div>
        <div class="env-actions">
          <button class="ghost" id="btnEnvLightOn">开灯</button>
          <button class="ghost" id="btnEnvLightOff">关灯</button>
          <button class="ghost" id="btnEnvFanOn">开风扇</button>
          <button class="ghost" id="btnEnvFanOff">关风扇</button>
        </div>
      </div>

      <div class="chat" id="chat"></div>''', 1)
    print("环境面板 HTML 已加")

    # 顶栏加温湿度小胶囊
    s = s.replace('<div class="clock" id="clock">--:--</div>',
                  '<div class="clock" id="clock">--:--</div>\n      <div class="envchip" id="envChip">--°C · --%</div>', 1)
    print("顶栏胶囊已加")

open(P, "w", encoding="utf-8").write(s)

C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if ".env-panel" not in cs:
    cs += '''

/* 顶栏环境胶囊 */
.envchip{font-size:12px;color:#9fe0ff;background:rgba(20,40,70,.6);
  border:1px solid rgba(127,212,255,.3);border-radius:999px;padding:5px 12px;white-space:nowrap}

/* 客房环境面板 */
.env-panel{margin:8px 14px 4px;padding:12px 14px;border-radius:14px;
  background:linear-gradient(150deg,rgba(18,34,60,.9),rgba(10,20,34,.9));
  border:1px solid rgba(127,212,255,.22)}
.env-head{display:flex;align-items:center;gap:8px;font-size:13px;color:#cfe3ff}
.env-dot{width:8px;height:8px;border-radius:50%;background:#5a6b85}
.env-dot.on{background:#3fe08a;box-shadow:0 0 8px rgba(63,224,138,.8)}
.env-state{font-size:11px;color:#8fa4c8}
.env-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin-top:10px}
.env-cell{background:rgba(255,255,255,.04);border-radius:10px;padding:6px 4px;text-align:center}
.env-cell span{display:block;font-size:10px;color:#8fa4c8}
.env-cell b{font-size:16px;color:#eaf2ff}
.env-cell i{font-size:10px;color:#8fa4c8;font-style:normal}
.env-actions{display:flex;gap:8px;margin-top:10px}
.env-actions .ghost{flex:1;font-size:12px;padding:8px 0;border-radius:10px}
.env-panel.alarm{border-color:rgba(255,110,130,.6);box-shadow:0 0 16px rgba(255,80,100,.25)}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("样式已加")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
if "bindHomeEnv" not in js:
    js += '''

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
'''
    open(J, "w", encoding="utf-8").write(js)
    print("前端逻辑已加")
