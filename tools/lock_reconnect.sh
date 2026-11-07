#!/bin/bash
PB=123456
echo "=== 开启门锁板自动重连 ==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock']['transport'] = 'auto'    # 自动扫描 + 掉线重连
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("lock.transport = auto")
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 22

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq2.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
print("  rfid :", (d.get('rfid') or {}).get('port'), (d.get('rfid') or {}).get('reads'))
PY
echo
echo "=== 探测日志 ==="
grep -aE '\[lock:board\]|\[port\]|\[home\] 找到' /opt/zhikong/logs/backend.log | tail -6
