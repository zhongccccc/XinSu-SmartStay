#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
rm -rf /tmp/csz
setsid nohup chromium-browser --ozone-platform=wayland --kiosk \
  --force-device-scale-factor=1 \
  --user-data-dir=/tmp/csz --no-first-run --test-type --disable-gpu \
  --password-store=basic \
  --app=http://127.0.0.1:8080/static/size.html \
  > /tmp/sz.log 2>&1 < /dev/null &
sleep 18
grim -o DSI-1 /tmp/sz.png && echo "shot ok"
