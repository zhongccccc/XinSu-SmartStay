#!/bin/bash
B=http://127.0.0.1:8080

st() { curl -s $B/api/state > /tmp/sx.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/sx.json'))
print("   step=%-6s code=%-7s card=%-10s msg=%s" % (d.get('step'), d.get('lock_code') or '-',
      d.get('card_uid') or '-', (d.get('msg') or '')[:30]))
PY
}

echo "=== 等家居板心跳 ==="
sleep 12
curl -s $B/api/home | python3 -c "
import sys,json
d=json.load(sys.stdin); x=d.get('data') or {}
print('   %s | 温度=%s 湿度=%s 光照=%s 燃气=%s' % (d.get('firmware'), x.get('temp'), x.get('hum'), x.get('lux'), x.get('gas')))
"

echo
echo "=== 办入住（含房卡步骤）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/9902 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.6
echo "  ↓ 支付后应停在房卡步骤"
st
echo "  ↓ 刷卡（模拟读卡器读到 CARD9902）"
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD9902"}' $B/api/card > /dev/null
sleep 6
st

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo
echo "=== 门锁板校验开门码 $CODE ==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo

echo
echo "=== 大堂刷卡退房（同一张卡）==="
curl -s -X POST $B/api/reset > /dev/null; sleep 1.5
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD9902"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('   在住订单数 =', len(d.get('inhouse') or []))
"
echo "=== 旧码应失效 ==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo
