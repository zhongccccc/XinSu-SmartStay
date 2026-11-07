# -*- coding: utf-8 -*-
"""在一体机界面底部显示当前 IP，方便换 WiFi 后找到它。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

ROUTE = '''            if p == "/api/net":
                ip, ssid = "", ""
                try:
                    out = subprocess.run(["hostname", "-I"], capture_output=True,
                                         text=True, timeout=2).stdout.split()
                    for x in out:
                        if ":" not in x and not x.startswith("127."):
                            ip = x
                            break
                except Exception:
                    pass
                try:
                    r = subprocess.run(["nmcli", "-t", "-f", "GENERAL.CONNECTION",
                                        "device", "show", "wlan0"],
                                       capture_output=True, text=True, timeout=2).stdout
                    if ":" in r:
                        ssid = r.strip().split(":", 1)[1]
                except Exception:
                    pass
                return self._json({"ip": ip, "ssid": ssid, "host": "shiqi.local"})
'''

if "/api/net" not in s:
    anchor = '            if p == "/api/home":'
    s = s.replace(anchor, ROUTE + anchor, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[main] /api/net 已加")
else:
    print("[main] 已存在")

# ---------- 前端：底部版本号处显示 IP ----------
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

if "showNet" not in js:
    js += '''

/* ---------- 底部显示当前 IP ---------- */
(function showNet() {
  const paint = (d) => {
    const v = document.querySelector('.devbar .ver');
    if (!v || !d) return;
    const ip = d.ip ? (' · ' + d.ip) : '';
    v.textContent = 'RISC-V K1 · Bianbu 2.3.5' + ip;
    v.title = (d.ssid ? ('WiFi: ' + d.ssid + '  ') : '') + 'ssh shiqi@' + (d.host || 'shiqi.local');
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
'''
    open(J, "w", encoding="utf-8").write(js)
    print("[js] IP 显示已加")
