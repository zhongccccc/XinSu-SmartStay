#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
rm -f /tmp/k2.log
setsid nohup chromium-browser --ozone-platform=wayland --kiosk \
  --window-position=0,0 --window-size=800,480 \
  --user-data-dir=/opt/zhikong/data/chromium-kiosk \
  --no-first-run --test-type --disable-gpu --password-store=basic \
  --app=http://127.0.0.1:8080/ > /tmp/k2.log 2>&1 < /dev/null &
sleep 18
echo "实例: $(pgrep -c -f chromium)"
grim /tmp/p4.png && echo "shot ok"
