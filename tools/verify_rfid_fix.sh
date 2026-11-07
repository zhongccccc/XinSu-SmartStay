#!/bin/bash
PB=123456
cd /opt/zhikong/app
python3 -m py_compile backend/devices/rfid_serial.py && echo "COMPILE_OK"

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 22

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/z1.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/z1.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), "mock=", lk.get('mock'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'))
print("  读卡器:", rf.get('port'), "online=", rf.get('online'), "reads=", rf.get('reads'))
PY
echo
echo "=== 观察 20 秒，看板子是否稳定（不再被干扰）==="
sleep 20
curl -s http://127.0.0.1:8080/api/health > /tmp/z2.json 2>/dev/null
python3 - <<'PY'
import json
d = json.load(open('/tmp/z2.json'))
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('online'), lk.get('firmware'))
print("  家居板:", hm.get('online'), hm.get('firmware'))
print("  读卡器: reads=", rf.get('reads'))
PY
echo
echo "=== 最近是否有 rfid 干扰日志 ==="
grep -a '\[rfid\]' /opt/zhikong/logs/backend.log | tail -4
