#!/bin/bash
PB=123456
pkill -9 -f chromium 2>/dev/null
sleep 3
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 40
echo "实例: $(pgrep -c -f 'chromium.*8080')"
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/repaired.png && echo "shot ok"
