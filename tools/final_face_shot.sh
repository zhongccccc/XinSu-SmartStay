#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 3
grim /tmp/face_final.png && echo shot ok
