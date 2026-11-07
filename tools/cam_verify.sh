#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== camera info ==="
curl -s -m 8 $B/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
print("camera:", d.get("camera"))
print("rfid  :", d.get("rfid"))
PY

echo "=== 快照 ==="
curl -s -m 8 -o /tmp/snap.jpg $B/api/camera/snapshot.jpg
ls -l /tmp/snap.jpg

echo "=== 进到人脸页并截图 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 2.5
grim /tmp/face_live.png && echo "shot ok"
curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=',d['step'])"
