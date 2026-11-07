#!/bin/bash
B=http://127.0.0.1:8080
curl -s http://127.0.0.1:8080/api/health > /tmp/hz4.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hz4.json'))
print("lock:", d.get('lock'))
PY
echo
echo "=== 办入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state > /tmp/st3.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/st3.json'))
print("step:", d.get('step'))
print("房间:", (d.get('room') or {}).get('no'))
print("开门码:", d.get('lock_code'))
PY
