#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080

LINES_BEFORE=$(grep -ac 'lock_checkout\|checkout' /opt/zhikong/logs/backend.out || true)
echo "点按前 checkout 日志行数: $LINES_BEFORE"

echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 84 313 2>&1 | tail -1
sleep 2
grim /tmp/co3.png
LINES_AFTER=$(grep -ac 'lock_checkout\|checkout' /opt/zhikong/logs/backend.out || true)
echo "点按后: $LINES_AFTER"
echo "--- 近期日志 ---"
tail -5 /opt/zhikong/logs/backend.out
