#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
echo "$PB" | sudo -S -p '' python3 /tmp/fp4.py
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 7
curl -s http://127.0.0.1:8080/api/health > /tmp/h9.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h9.json'))
print("lock:", d.get('lock'))
PY
