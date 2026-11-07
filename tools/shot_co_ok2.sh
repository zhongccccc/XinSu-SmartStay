#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo ">>> 当前在住"
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  ', [(o['room'],o['card_uid']) for o in (d.get('inhouse') or [])])"

echo ">>> 用 8802 + CARD8802 办入住"
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8802 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8802"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d.get('step'),'code=',d.get('lock_code'))"
curl -s -X POST $B/api/reset > /dev/null
sleep 1.5

echo ">>> 刷 CARD8802 退房"
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8802"}' $B/api/card > /dev/null
sleep 1.5
grim /tmp/co_ok2.png && echo "截图完成"
