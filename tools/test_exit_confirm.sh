#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
echo "=== 点「退出到桌面」(425,273) ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 425 273 1 0.06
sleep 4
echo "  chromium 剩余: $(pgrep -c -f 'chromium.*8080')"
echo "  后端: $(systemctl is-active zhikong-backend)"
grim /tmp/back_to_desktop.png && echo "shot ok"
grep -E "kiosk exit" /opt/zhikong/logs/backend.out | tail -2
