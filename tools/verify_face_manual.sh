#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 14
for i in $(seq 1 30); do curl -s -m 1 -o /dev/null $B/api/health && break; sleep 1; done

curl -s -X POST $B/api/cancel > /dev/null; sleep 1

echo "=== 身份证页 ==="
curl -s -X POST $B/api/session/start > /dev/null
sleep 4
grim -o DSI-1 /tmp/p_ident.png && echo "  shot"

echo "=== 人脸页 ==="
curl -s -X POST $B/api/idcard/mock > /dev/null
sleep 5
grim -o DSI-1 /tmp/p_face.png && echo "  shot"

echo "=== 状态（应停在人脸页，不自动跳）==="
sleep 8
curl -s $B/api/state | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  step=%s (应为 face)' % d.get('step'))
"
grim -o DSI-1 /tmp/p_face2.png && echo "  8 秒后再拍一张（确认没自动跳）"
