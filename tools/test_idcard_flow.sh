#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 等后端稳定轮询 ==="
sleep 10
curl -s -m 8 $B/api/health > /tmp/h2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h2.json'))
print("idcard:", d.get("idcard"))
PY

echo "=== 开始入住 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null
sleep 1
curl -s $B/api/state | python3 -c "import sys,json;print('step=',json.load(sys.stdin)['step'])"

echo "=== 等真卡被读到（最多 30 秒）==="
for i in $(seq 1 15); do
  sleep 2
  s=$(curl -s -m 4 $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])" 2>/dev/null)
  echo "  ${i}: step=$s"
  [ "$s" = "face" ] && break
done

echo "=== 结果 ==="
curl -s $B/api/state | python3 - <<'PY'
import sys, json
d = json.load(sys.stdin)
print("step =", d["step"])
print("guest=", d.get("guest"))
print("idno =", d.get("idno"))
print("camera_ok =", d.get("camera_ok"))
PY
echo "=== 后端日志 ==="
grep -E "\[idcard\]" /opt/zhikong/logs/backend.out | tail -3
grim /tmp/idcard_flow.png && echo "shot ok"
