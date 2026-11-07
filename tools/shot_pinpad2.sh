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

echo "=== 点「门锁键盘（演示）」 ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 720 273 2>&1 | tail -1
sleep 1.2
grim /tmp/p7.png && echo "pinpad shot"

echo "=== 依次点 6 1 2 6 1 7 # ==="
for pair in "367 300" "310 300" "423 300" "367 300" "310 300" "480 300"; do
  set -- $pair
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1
  sleep 0.5
done
sleep 2
grim /tmp/p8.png && echo "after pin shot"
