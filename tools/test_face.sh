#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.6
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 3
echo "=== 状态 ==="
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d.get('step'))"
sleep 3
grim -o DSI-1 /tmp/face_page.png && echo "截图完成"
echo "=== 摄像头进程 ==="
pgrep -a gst-launch-1.0 2>/dev/null | head -2
pgrep -a python3 2>/dev/null | grep -c backend | sed 's/^/  backend 进程: /'
