#!/bin/bash
PB=123456
echo "=== 杀掉占用串口的残留进程 ==="
echo "$PB" | sudo -S -p '' kill -9 157619 2>/dev/null
sleep 1
echo "$PB" | sudo -S -p '' fuser -v /dev/ttyUSB0 2>&1 | head -4
echo "=== 重启后端 ==="
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 4
curl -s -m 6 http://127.0.0.1:8080/api/health > /tmp/h3.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h3.json'))
print("rfid  :", d.get("rfid"))
print("camera:", d.get("camera"))
PY
echo "=== rfid 日志 ==="
grep -E "\[rfid\]|\[camera\]" /opt/zhikong/logs/backend.out | tail -6
