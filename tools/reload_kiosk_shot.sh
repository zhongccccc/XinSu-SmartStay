#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 12
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 3
grim /tmp/face_live3.png && echo shot ok
curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=',d['step'],'camera_ok=',d.get('camera_ok'))"
