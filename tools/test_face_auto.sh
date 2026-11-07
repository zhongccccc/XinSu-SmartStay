#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 回待机 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.5
echo "=== 开始入住 ==="
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
echo "=== 刷身份证 ==="
curl -s -X POST $B/api/idcard/mock > /dev/null
sleep 1.5
echo "--- 此刻应停在人脸页 ---"
curl -s $B/api/state > /tmp/f1.json
python3 -c "import json;d=json.load(open('/tmp/f1.json'));print('   step =', d.get('step'))" 2>/dev/null || true
grim -o DSI-1 /tmp/face_auto_1.png

echo "=== 等 4 秒（前端应自动放行）==="
sleep 4
curl -s $B/api/state > /tmp/f2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/f2.json'))
print("   step =", d.get("step"), "|", (d.get("msg") or "")[:30])
PY
grim -o DSI-1 /tmp/face_auto_2.png
echo "截图完成"
