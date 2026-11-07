#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

step() { curl -s $B/api/state > /tmp/st.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/st.json'))
print("   step=%-6s code=%-7s msg=%s" % (d.get('step'), d.get('lock_code') or '-', (d.get('msg') or '')[:36]))
PY
}
home() { curl -s $B/api/home > /tmp/hm.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/hm.json'))
x = d.get('data') or {}
print("   家居板: online=%s fw=%s | 温度=%s 湿度=%s 光照=%s 燃气=%s 人体=%s 灯=%s 风扇=%s"
      % (d.get('online'), d.get('firmware'), x.get('temp'), x.get('hum'), x.get('lux'),
         x.get('gas'), x.get('pir'), x.get('light'), x.get('fan')))
PY
}

echo "=========== 1. 归零 ==========="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2; step

echo "=========== 2. 办入住 ==========="
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8806"}' $B/api/card > /dev/null
sleep 6
step
home

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "   开门码 = $CODE"

echo "=========== 3. 门锁板本地校验开门码 ==========="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo

echo "=========== 4. 凭码退房 ==========="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/checkout | head -c 120
echo
sleep 4
step
home

echo "=========== 5. 旧码应被拒 ==========="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/lock/code
echo
