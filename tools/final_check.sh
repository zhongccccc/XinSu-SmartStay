#!/bin/bash
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 2
curl -s -m 8 http://127.0.0.1:8080/api/health > /tmp/hf.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hf.json'))
c = d['camera']
r = d['rfid']
print("camera:", c['ok'], c['node'], "fps", c['fps'])
print("rfid  :", r['online'], r.get('last_uid'))
print("lock  :", d.get('lock'))
PY
