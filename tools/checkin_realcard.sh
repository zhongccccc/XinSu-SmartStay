#!/bin/bash
B=http://127.0.0.1:8080
CARD="${1:-0AD21E00}"

echo "=== 办入住（房卡用真实卡号 $CARD）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d "{\"uid\":\"$CARD\"}" $B/api/card > /dev/null
sleep 4

curl -s $B/api/state > /tmp/stx.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/stx.json'))
print("step:", d.get('step'))
print("房间:", (d.get('room') or {}).get('no'))
print("开门码:", d.get('lock_code'))
PY
echo
echo "=== 回待机（保留凭证）==="
curl -s -X POST $B/api/reset > /dev/null
sleep 1
echo "完成，请到门锁板刷这张卡"
