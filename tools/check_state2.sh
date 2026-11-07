#!/bin/bash
echo "=== 最近门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -22
echo
echo "=== 健康状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h6.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h6.json'))
print("  lock:", d.get('lock'))
PY
echo
echo "=== 当前订单（最近 3 条）==="
curl -s http://127.0.0.1:8080/api/state > /tmp/s6.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/s6.json'))
print("  step:", d.get('step'), " code:", d.get('lock_code'))
for o in (d.get('inhouse') or [])[:3]:
    print("   ", o.get('room'), o.get('lock_code'), o.get('status'))
PY
