#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4
grim /tmp/done_screen.png && echo "done screen ok"
