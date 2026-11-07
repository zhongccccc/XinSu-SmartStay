#!/bin/bash
B=http://127.0.0.1:8080

echo "=== 1. 办两间房：8808 / 8802 ==="
for R in 8808 8802; do
  curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
  curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
  curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
  curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
  curl -s -X POST $B/api/room/$R > /dev/null; sleep 0.3
  curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
  curl -s -X POST -H 'Content-Type: application/json' -d "{\"uid\":\"CARD-$R\"}" $B/api/card > /dev/null
  sleep 4
  curl -s $B/api/state > /tmp/s_$R.json
  python3 - "$R" <<'PY'
import json, sys
r = sys.argv[1]
d = json.load(open('/tmp/s_%s.json' % r))
print("  房间 %s  step=%s  码=%s" % (r, d.get('step'), d.get('lock_code')))
PY
  curl -s -X POST $B/api/reset > /dev/null
  sleep 0.5
done

echo
echo "=== 2. 订房页里的占用状态 ==="
curl -s $B/api/state > /tmp/sx.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/sx.json'))
occ = [r['no'] for r in (d.get('rooms') or []) if r.get('occupied')]
print("  已订房:", occ)
PY

echo
echo "=== 3. 退掉 8808，看 8802 是否仍有效 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"room":"8808"}' $B/api/checkout > /dev/null
sleep 2
C8802=$(python3 -c "import json;print(json.load(open('/tmp/s_8802.json')).get('lock_code'))")
C8808=$(python3 -c "import json;print(json.load(open('/tmp/s_8808.json')).get('lock_code'))")
echo "  8808 的码 $C8808 是否失效？"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$C8808\"}" $B/api/lock/code; echo
echo "  8802 的码 $C8802 是否仍有效？"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$C8802\"}" $B/api/lock/code; echo

echo
echo "=== 4. 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -6
