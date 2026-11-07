#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1; sleep 1.2; }
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('   step=%s guest=%s room=%s' % (d['step'], d.get('guest'), (d.get('room') or {}).get('no')))"; }

echo "=== 重载 kiosk ==="
pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 13

echo "=== 走到 人脸 步骤 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 1.2
st
grim /tmp/back_before.png

echo "=== 点右上角「‹ 返回」 ==="
tap 670 24
st
grim /tmp/back_after.png

echo "=== 点击命中 ==="
grep -E "\[ui\]" /opt/zhikong/logs/backend.out | tail -3
