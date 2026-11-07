#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
pkill -f 'chromium.*8080' 2>/dev/null
sleep 2
nohup chromium-browser --ozone-platform=wayland --disable-gpu --no-first-run \
  --force-device-scale-factor=1 --window-position=0,0 --window-size=800,480 \
  --app='http://127.0.0.1:8080/?admin=1' > /tmp/kiosk_adm.log 2>&1 &
sleep 14
grim -o DSI-1 /tmp/adm_screen.png && echo "shot ok"
