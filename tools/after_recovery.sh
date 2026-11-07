#!/bin/bash
PB=123456
echo "=== 网络 ==="
ip -br addr | grep -v '^lo'
nmcli -t -f GENERAL.CONNECTION device show wlan0 2>/dev/null | head -2

echo
echo "=== 服务 ==="
echo "  backend: $(systemctl is-active zhikong-backend)"
echo "  kiosk  : $(pgrep -c -f 'chromium.*8080') 个进程"
curl -s -o /dev/null -w '  HTTP: %{http_code}\n' http://127.0.0.1:8080/api/health

echo
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hn.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hn.json'))
except Exception as e:
    print("  health 读不到:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), "mock=", lk.get('mock'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'))
print("  读卡器:", rf.get('port'), "online=", rf.get('online'))
PY

echo
echo "=== 加固：WiFi 开机自动连接 ==="
echo "$PB" | sudo -S -p '' nmcli connection modify "非洲之星-plus" connection.autoconnect yes 2>/dev/null \
  && echo "  已设 autoconnect=yes"
echo "$PB" | sudo -S -p '' nmcli connection modify "非洲之星-plus" connection.autoconnect-priority 10 2>/dev/null \
  && echo "  已设优先级 10"
echo "$PB" | sudo -S -p '' nmcli -t -f connection.autoconnect,connection.autoconnect-priority connection show "非洲之星-plus" 2>/dev/null | sed 's/^/  /'
