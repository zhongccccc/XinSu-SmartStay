#!/bin/bash
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/state_ok.png && echo "shot ok"
