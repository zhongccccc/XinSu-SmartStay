#!/bin/bash
PB=123456
cd /opt/zhikong/app
python3 -m py_compile backend/main.py backend/devices/home_board.py backend/devices/lock.py && echo "COMPILE_OK"

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 26

echo "=== 端口认领日志 ==="
grep -a '\[port\]' /opt/zhikong/logs/backend.log | tail -6

echo
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/f1.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/f1.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), "mock=", lk.get('mock'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'), hm.get('firmware'))
print("  读卡器:", rf.get('port'), "online=", rf.get('online'))
PY
