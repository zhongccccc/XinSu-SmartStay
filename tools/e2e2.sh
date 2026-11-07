#!/bin/bash
B=http://127.0.0.1:8080
j() { echo "$1" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('step'),d.get('lock_code') or '-')"; }
chk() { python3 -c "
import json,urllib.request
req=urllib.request.Request('$B/api/lock/code',data=json.dumps({'pin':'$1'}).encode(),headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
"; }

echo "=== 办入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8809 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8809"}' $B/api/card > /dev/null
sleep 4
CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "  开门码=$CODE"

echo "=== 「完成并返回」→ /api/reset（应保留凭证）==="
curl -s -X POST $B/api/reset > /dev/null; sleep 1.5
echo "  校验 $CODE: $(chk $CODE)"

echo
echo "=== 「退房」→ /api/checkout（应作废凭证）==="
curl -s -X POST $B/api/checkout > /dev/null; sleep 2
echo "  校验 $CODE: $(chk $CODE)"

echo
echo "=== 事件 ==="
grep -a 'lock_checkout\|CODE:' /opt/zhikong/logs/backend.out | tail -6
