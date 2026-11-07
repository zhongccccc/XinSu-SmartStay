#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1; sleep 1.3; }
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s guest=%s' % (d['step'], d.get('guest')))"; }

curl -s -X POST $B/api/cancel > /dev/null; sleep 1
echo "点『触摸屏幕开始入住』"
tap 180 275
st
echo "模拟刷证 -> 人脸页"
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 1.5
st
grim /tmp/app_face_back.png

echo "点右上角返回"
tap 645 24
st
grim /tmp/app_after_back.png
grep -E "\[ui\] (down|click)" /opt/zhikong/logs/backend.out | tail -2
