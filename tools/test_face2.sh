#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 触发人脸核验 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":true}' $B/api/face | head -c 220
echo
sleep 3
echo "=== 结果状态 ==="
curl -s $B/api/state > /tmp/st_face.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/st_face.json'))
print("  step =", d.get("step"))
print("  msg  =", (d.get("msg") or "")[:50])
print("  face =", d.get("face"))
PY
echo "=== 错误日志 ==="
grep -aEi 'face|error|Traceback' /opt/zhikong/logs/backend.log | tail -6
