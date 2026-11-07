#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
PB=123456

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.5
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 3
echo "state: $(curl -s $B/api/state | python3 -c 'import sys,json;print(json.load(sys.stdin)["step"])')"
grim /tmp/d4.png && echo shot1
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 745 252 > /dev/null 2>&1
sleep 1.2
grim /tmp/p4.png && echo shot2
