#!/bin/bash
pkill -f 'user-data-dir=/tmp/chrome-adm' 2>/dev/null
pkill -f 'chromium.*8080' 2>/dev/null
sleep 2
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 15
echo "chromium: $(pgrep -c -f 'chromium.*8080')"
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/final_idle.png && echo "shot ok"
