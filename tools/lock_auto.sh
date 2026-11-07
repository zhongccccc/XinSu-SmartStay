#!/bin/bash
PB=123456
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock']['transport'] = 'auto'      # 允许自动发现/重连
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("lock.transport = auto")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 25
tr -d '\r' < /tmp/sc.sh | bash
echo
echo "=== 后端探测日志 ==="
grep -aE '\[lock|\[home' /opt/zhikong/logs/backend.log | tail -6
