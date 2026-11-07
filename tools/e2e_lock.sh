#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
st() { curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('step'),d.get('lock_code') or '-')"; }

echo "=== 1. 重置 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
echo "  state: $(st)"

echo "=== 2. 办入住 ==="
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 4
CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "  state: $(st)   开门码=$CODE"

echo "=== 3. 板端校验正确码 ==="
echo -n "  "; echo "$PB" | sudo -S -p '' python3 -c "
import sys,json,urllib.request
req=urllib.request.Request('$B/api/lock/code',data=json.dumps({'pin':'$CODE'}).encode(),headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
"
sleep 3

echo "=== 4. 板端校验错误码 ==="
echo -n "  "; echo "$PB" | sudo -S -p '' python3 -c "
import json,urllib.request
req=urllib.request.Request('$B/api/lock/code',data=json.dumps({'pin':'000000'}).encode(),headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
"
sleep 1

echo "=== 5. 退房（作废凭证）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 2
echo "  state: $(st)"

echo "=== 6. 用旧码再校验（应被拒）==="
echo -n "  "; echo "$PB" | sudo -S -p '' python3 -c "
import json,urllib.request
req=urllib.request.Request('$B/api/lock/code',data=json.dumps({'pin':'$CODE'}).encode(),headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
"

echo
echo "=== 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -12
