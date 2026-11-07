#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1; sleep 1.2; }

curl -s -X POST $B/api/cancel > /dev/null
sleep 1
echo "打开语音面板"
tap 731 24
echo "点『开灯』"
tap 107 400
sleep 2.5
grim /tmp/voice_dup.png && echo "shot ok"
grep -E "\[voice\]" /opt/zhikong/logs/backend.out | tail -2
