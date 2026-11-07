#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f rfid_poll.py 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f "zhikong/app/tools/rfid" 2>/dev/null
sleep 1
echo "=== 剩余占用 ==="
echo "$PB" | sudo -S -p '' fuser -v /dev/ttyUSB0 2>&1 | head -4
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 3
echo "=== rfid 状态 ==="
curl -s -m 6 http://127.0.0.1:8080/api/health > /tmp/h2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h2.json'))
print("rfid  :", d.get("rfid"))
print("camera:", d.get("camera"))
PY
echo "=== rfid 日志 ==="
grep -E "\[rfid\]" /opt/zhikong/logs/backend.out | tail -4
