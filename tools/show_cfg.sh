#!/bin/bash
echo "=== config.devices ==="
python3 - <<'PY'
import json
d = json.load(open('/opt/zhikong/etc/config.json'))
print(json.dumps(d.get('devices'), ensure_ascii=False, indent=2))
PY
echo
echo "=== build_lock ==="
grep -n 'def build_lock' -A 14 /opt/zhikong/app/backend/devices/lock.py | head -18
