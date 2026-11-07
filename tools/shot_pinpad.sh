#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
PB=123456

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4
grim /tmp/done3.png && echo "done shot ok"

echo "=== 点开门锁键盘按钮 ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 742 250 > /dev/null 2>&1
sleep 1.5
grim /tmp/pinpad.png && echo "pinpad shot ok"
