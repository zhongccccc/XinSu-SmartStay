#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== RFID 现场读一次（卡可能已被拿走）==="
echo 123456 | sudo -S -p '' timeout 20 python3 /opt/zhikong/app/tools/rfid_poll.py 6 2>&1 | tail -5

echo
echo "=== 人脸页实拍 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.6
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 2.5
grim /tmp/face_live2.png && echo shot ok
curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=',d['step'],'camera_ok=',d.get('camera_ok'))"
echo "$PB_PLACEHOLDER" > /dev/null
