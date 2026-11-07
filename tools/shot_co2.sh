#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 85 312 > /dev/null 2>&1
sleep 1.5
grim /tmp/co2.png && echo shot_ok
