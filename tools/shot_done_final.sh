#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

if ! pgrep -f '[c]hromium.*8080' > /dev/null; then
  setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/al3.log 2>&1 < /dev/null &
  sleep 15
fi

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 4
grim /tmp/done_final.png && echo shot_ok
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=',d.get('step'),'code=',d.get('lock_code'))"
