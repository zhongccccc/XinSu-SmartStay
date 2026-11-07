#!/bin/bash
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 后端设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hz.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hz.json'))
except Exception as e:
    print("  读不到 health:", e); raise SystemExit
print("  rfid :", d.get('rfid'))
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'))
print("  home :", hm.get('port'), hm.get('online'))
PY
echo
echo "=== rfid 配置 ==="
python3 - <<'PY'
import json
c = json.load(open('/opt/zhikong/etc/config.json'))
print(json.dumps(c.get('devices'), ensure_ascii=False))
PY
