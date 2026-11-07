#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
rm -rf /tmp/chrome-win
setsid nohup chromium-browser --ozone-platform=wayland \
  --window-position=0,0 --window-size=800,480 \
  --user-data-dir=/tmp/chrome-win --no-first-run --test-type --disable-gpu \
  --password-store=basic --app=http://127.0.0.1:8080/ \
  > /tmp/kwin.log 2>&1 < /dev/null &
sleep 18
grim /tmp/win_view.png && echo "shot ok"
