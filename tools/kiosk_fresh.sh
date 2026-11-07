#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
rm -rf /opt/zhikong/data/chromium-kiosk
mkdir -p /opt/zhikong/data/chromium-kiosk
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
setsid nohup chromium-browser --ozone-platform=wayland --kiosk \
  --window-position=0,0 --window-size=800,480 \
  --user-data-dir=/opt/zhikong/data/chromium-kiosk \
  --no-first-run --test-type --disable-gpu --password-store=basic \
  --disk-cache-size=1 --media-cache-size=1 \
  --app=http://127.0.0.1:8080/ > /tmp/k3.log 2>&1 < /dev/null &
sleep 20
grim /tmp/p6.png && echo "shot ok"
