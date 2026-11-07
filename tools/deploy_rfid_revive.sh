#!/bin/bash
PB=123456
cd /opt/zhikong/app
python3 -m py_compile backend/devices/rfid_serial.py && echo "COMPILE_OK"
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 14
curl -s http://127.0.0.1:8080/api/health > /tmp/hr9.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hr9.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
rf = d.get('rfid') or {}
print("  rfid:", rf.get('port'), rf.get('online'), "reads=", rf.get('reads'))
PY
echo
echo "=== 重开日志（若 60 秒无卡会出现）==="
sleep 65
grep -a '\[rfid\]' /opt/zhikong/logs/backend.log | tail -4
echo "  现在: $(date '+%H:%M:%S')"
