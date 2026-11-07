#!/bin/bash
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo "=== 服务 ==="
systemctl is-active zhikong-backend
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h6.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/h6.json'))
except Exception:
    print("  后端未就绪"); raise SystemExit
print("  rfid  :", d.get('rfid'))
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  lock  :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home  :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
