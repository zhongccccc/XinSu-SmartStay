#!/bin/bash
PB=123456
echo "=== 重启后端（自动认领端口）==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 24

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq5.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq5.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'), hm.get('firmware'))
print("  读卡器:", rf.get('port'), "reads=", rf.get('reads'))
PY
echo
echo "=== 家居板数据 ==="
curl -s http://127.0.0.1:8080/api/home | head -c 260
echo
