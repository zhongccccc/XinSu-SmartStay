#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 24
echo "=== 家居板 ==="
curl -s http://127.0.0.1:8080/api/home | head -c 260
echo
echo
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hr2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hr2.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; c = d.get('camera') or {}
rf = d.get('rfid') or {}
print("  camera:", c.get('ok'))
print("  lock  :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home  :", hm.get('port'), hm.get('online'), hm.get('firmware'))
print("  rfid  :", rf.get('port'), rf.get('online'), "reads=", rf.get('reads'))
PY
echo
echo "=== 家居板日志 ==="
grep -a '\[home\] 找到板子' /opt/zhikong/logs/backend.log | tail -2
