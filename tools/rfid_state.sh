#!/bin/bash
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq.json'))
except Exception as e:
    print("  health 读不到:", e); raise SystemExit
print("  rfid :", d.get('rfid'))
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
echo
echo "=== rfid 日志（最近） ==="
grep -a '\[rfid\]' /opt/zhikong/logs/backend.log | tail -6
echo
echo "=== 100 秒内是否有卡 ==="
grep -ac 'card uid' /opt/zhikong/logs/backend.log 2>/dev/null
