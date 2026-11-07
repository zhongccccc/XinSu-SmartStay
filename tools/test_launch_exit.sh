#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" "${3:-1}" "${4:-0.06}" 2>&1 | tail -1; sleep "${5:-2.5}"; }

echo "=== 当前：桌面，无界面进程 ==="
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"

echo "=== 单击图标 (200,55) ==="
tap 200 55 1 0.06 8
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"
pgrep -af "chromium.*8080" | head -1 | cut -c1-60
grim /tmp/single_launch.png && echo "  shot ok"

echo "=== 长按 logo 1.8 秒 ==="
tap 32 24 1 1.8 1.5
grim /tmp/exit_mask.png && echo "  shot ok"

echo "=== 点「退出到桌面」 ==="
tap 452 292 1 0.06 4
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"
grim /tmp/after_exit.png && echo "  shot ok"
