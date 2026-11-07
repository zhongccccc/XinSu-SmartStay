#!/bin/bash
echo "=== 最近门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -25
echo
echo "=== 串口 ==="
ls -l /dev/ttyUSB2 2>/dev/null
echo
echo "=== 健康 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h2.json'))
print("  lock:", d.get('lock'))
PY
