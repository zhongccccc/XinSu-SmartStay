#!/bin/bash
PB=123456
cd /opt/zhikong/app
python3 -m py_compile backend/devices/lock.py && echo "COMPILE_OK"

python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices'].setdefault('lock', {})
d['devices']['lock']['transport'] = 'auto'    # 自动找端口（会扫描）
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("lock.transport = auto")
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 26

curl -s http://127.0.0.1:8080/api/health > /tmp/r2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/r2.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}
print("  门锁: port=%s online=%s mock=%s fw=%s" % (
    lk.get('port'), lk.get('online'), lk.get('mock'), lk.get('firmware')))
PY

echo
echo "=== 重新下发在住订单 ==="
curl -s -X POST http://127.0.0.1:8080/api/lock/resync | head -c 300
echo
