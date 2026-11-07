# -*- coding: utf-8 -*-
"""底部版本号后面带上当前 IP（devbar 每次重建都会重绘，所以放在这里）。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

# 1) 全局 NET 变量
if "let NET =" not in js:
    js = js.replace("let DEVICES = null;", "let DEVICES = null;\nlet NET = { ip: '', ssid: '', host: 'shiqi.local' };", 1)
    print("[1] NET 变量已加")

# 2) devbar 里带上 IP
OLD = """  const v = document.createElement('div'); v.className = 'ver';
  v.textContent = 'RISC-V K1 · Bianbu 2.3.5';
  bar.appendChild(v);"""
NEW = """  const v = document.createElement('div'); v.className = 'ver';
  v.textContent = 'RISC-V K1 · Bianbu 2.3.5' + (NET.ip ? (' · ' + NET.ip) : '');
  v.title = (NET.ssid ? ('WiFi: ' + NET.ssid + '   ') : '') + 'ssh shiqi@' + (NET.host || 'shiqi.local');
  bar.appendChild(v);"""
if OLD in js:
    js = js.replace(OLD, NEW, 1)
    print("[2] devbar 已带 IP")

# 3) showNet 里更新 NET 并重绘 devbar
OLD2 = """  const paint = (d) => {
    const v = document.querySelector('.devbar .ver');
    if (!v || !d) return;
    const ip = d.ip ? (' · ' + d.ip) : '';
    v.textContent = 'RISC-V K1 · Bianbu 2.3.5' + ip;
    v.title = (d.ssid ? ('WiFi: ' + d.ssid + '  ') : '') + 'ssh shiqi@' + (d.host || 'shiqi.local');
  };"""
NEW2 = """  const paint = (d) => {
    if (!d) return;
    NET = { ip: d.ip || '', ssid: d.ssid || '', host: d.host || 'shiqi.local' };
    renderDevices(DEVICES);      /* 重建 devbar，带上 IP */
  };"""
if OLD2 in js:
    js = js.replace(OLD2, NEW2, 1)
    print("[3] showNet 已改为重绘 devbar")

open(J, "w", encoding="utf-8").write(js)
print("done")
