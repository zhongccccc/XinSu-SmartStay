#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 拉起 kiosk ==="
setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/al2.log 2>&1 < /dev/null &
sleep 15
pgrep -c -f '[c]hromium.*8080' | sed 's/^/  chromium: /'

echo "=== 跑到完成页 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.5
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 3
grim /tmp/d6.png && echo "done shot"

echo "=== 点击门锁键盘按钮 ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 700 250 2>&1 | tail -1
sleep 1.5
grim /tmp/p6.png && echo "pinpad shot"
