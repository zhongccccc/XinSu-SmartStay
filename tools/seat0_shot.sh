#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
echo "--- chromium ---"
pgrep -af "chromium.*8080" | head -3
echo "--- kiosk log ---"
tail -8 /opt/zhikong/logs/kiosk_seat0.log 2>/dev/null
echo "--- grim ---"
grim -o DSI-1 /tmp/seat0.png 2>/dev/null || grim /tmp/seat0.png 2>&1 | head -3
ls -l /tmp/seat0.png 2>/dev/null
echo "--- outputs ---"
wlr-randr 2>/dev/null | head -12
