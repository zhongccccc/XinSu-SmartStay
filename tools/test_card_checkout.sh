#!/bin/bash
B=http://127.0.0.1:8080

echo "=== 1. 办入住（房卡 CARD8808）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 4
CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "  开门码=$CODE"

echo "=== 2. 回待机 ==="
curl -s -X POST $B/api/reset > /dev/null; sleep 1
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d.get('step'),' 在住=',len(d.get('inhouse') or []))"

echo "=== 3. 刷卡退房（模拟读卡器读到 CARD8808）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 3
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  退房后在住=',len(d.get('inhouse') or []))"

echo "=== 4. 凭证是否已作废 ==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code; echo

echo "=== 5. 刷一张没入住的卡 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"DEADBEEF"}' $B/api/card > /dev/null
sleep 1

echo
echo "=== 审计 ==="
echo 123456 | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for kind, payload in c.execute("SELECT kind, payload FROM audit WHERE kind IN ('lock_checkout','checkout_denied') ORDER BY id DESC LIMIT 4"):
    print("  %-18s %s" % (kind, payload[:100]))
c.close()
PY
