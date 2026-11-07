#!/bin/bash
echo "等待 20 秒，请把手指按在指纹传感器上（按 2 秒后抬起）…"
sleep 20
echo
echo "=== 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -12
echo
echo "=== 门锁状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h4.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h4.json'))
print("  lock:", d.get('lock'))
PY
