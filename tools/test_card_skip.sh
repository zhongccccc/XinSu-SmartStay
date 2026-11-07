#!/bin/bash
B=http://127.0.0.1:8080

st() { curl -s $B/api/state > /tmp/sk.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/sk.json'))
print("   step=%-6s code=%-7s card=%s msg=%s" % (d.get('step'), d.get('lock_code') or '-',
      d.get('card_uid') or '-', (d.get('msg') or '')[:26]))
PY
}

curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/9905 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.8

echo "=== 支付后（应停在房卡，等 20 秒自动放行）==="
st
echo "=== 等 8 秒 ==="; sleep 8; st
echo "=== 再等 15 秒（超时后应自动继续）==="; sleep 15; st
