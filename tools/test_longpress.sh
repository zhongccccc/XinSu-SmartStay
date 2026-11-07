#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 长按左上角 logo 1.8 秒 ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 32 24 1 1.8
sleep 2
grim /tmp/exit_mask2.png && echo "shot ok"
grep -E "\[ui\] (down|click)" /opt/zhikong/logs/backend.out | tail -3
