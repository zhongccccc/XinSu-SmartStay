#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
rm -rf /tmp/capp
setsid nohup chromium-browser --ozone-platform=wayland --kiosk \
  --force-device-scale-factor=1 \
  --user-data-dir=/tmp/capp --no-first-run --test-type --disable-gpu \
  --password-store=basic --app=http://127.0.0.1:8080/ \
  > /tmp/capp.log 2>&1 < /dev/null &
sleep 20
grim -o DSI-1 /tmp/app_now.png && echo "shot ok"
