#!/bin/bash
B=http://127.0.0.1:8080

st() { curl -s $B/api/state > /tmp/sq.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/sq.json'))
print("   step=%-6s code=%s card=%s" % (d.get('step'), d.get('lock_code') or '-', d.get('card_uid') or '-'))
PY
}

echo "=== 1. 办入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.5
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8801 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.8
echo "   （房卡步骤：等 20 秒自动放行，或刷卡）"
sleep 23
st
CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "   开门码 = $CODE"

echo
echo "=== 2. 正确密码（门锁板本地校验）==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo

echo "=== 3. 错误密码（应被拒 + 板子上报 CODEBAD）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"000000"}' $B/api/lock/code
echo
sleep 1
echo "   最近门锁事件:"
grep -aE 'ZK\|EVT\|CODE' /opt/zhikong/logs/backend.log | tail -4

echo
echo "=== 4. 家居板数据 ==="
curl -s $B/api/home | python3 -c "
import sys,json
d=json.load(sys.stdin); x=d.get('data') or {}
print('   %s 温度=%s 湿度=%s 光照=%s 燃气=%s 人体=%s' % (d.get('firmware'), x.get('temp'), x.get('hum'), x.get('lux'), x.get('gas'), x.get('pir')))
"

echo
echo "=== 5. 清理 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1
st
