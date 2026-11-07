#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.6
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 3.5
grim -o DSI-1 /tmp/ui_face.png && echo "人脸页已截"

echo "--- 点跳过（走接口，等价按钮）---"
curl -s -X POST -H 'Content-Type: application/json' -d '{"skip":true}' $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%s 结论=%s 分数=%s' % (d.get('step'), f.get('decision'), f.get('score')))
"
sleep 2
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.5
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"T"}' $B/api/pay > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARDX"}' $B/api/card > /dev/null; sleep 5
grim -o DSI-1 /tmp/ui_done.png && echo "完成页已截"

echo "--- 普通模式底栏 ---"
curl -s -X POST $B/api/cancel > /dev/null; sleep 2
grim -o DSI-1 /tmp/ui_idle.png && echo "待机页已截"
