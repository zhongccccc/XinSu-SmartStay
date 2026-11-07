#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 入住流程（凭证下发到门锁板）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
STEP=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('step'))")
echo "  step=$STEP  开门码=$CODE"

echo
echo "=== 板端校验：正确码 $CODE ==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo

echo "=== 板端校验：错误码 000000 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"000000"}' $B/api/lock/code
echo

echo
echo "=== 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -8
