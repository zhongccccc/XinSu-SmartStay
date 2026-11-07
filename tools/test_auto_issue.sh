#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%-6s code=%s order=%s' % (d['step'], d.get('lock_code'), d.get('order_id')))"; }

echo "=== 准备到「房卡」步骤 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.4
curl -s -X POST $B/api/room/8802 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.4
st

echo "=== 只调 /api/card，不调 /api/issue，看是否自动下发 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"TESTCARD01"}' $B/api/card > /dev/null
for i in $(seq 1 10); do
  sleep 0.5
  s=$(curl -s -m 4 $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])" 2>/dev/null)
  echo "  ${i}: step=$s"
  [ "$s" = "done" ] && break
done
echo "=== 最终 ==="
st
grim /tmp/issue_fix.png && echo "shot ok"
