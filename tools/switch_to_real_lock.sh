#!/bin/bash
# 配置切回真实门锁板（/dev/ttyUSB1），auto 模式：板子没固件时自动用 mock
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {}).setdefault('lock', {}).update(
    {"transport": "auto", "port": "/dev/ttyUSB1", "baud": 115200})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("lock =", d['devices']['lock'])
PY
pkill -f lock_board_sim 2>/dev/null
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -2
sleep 3
echo "=== 门锁状态（真板子没固件，应自动退化 mock）==="
curl -s http://127.0.0.1:8080/api/health | python3 -c "import sys,json;print('  ', json.load(sys.stdin).get('lock'))"
echo "=== 后端日志 ==="
grep -E "lock" /opt/zhikong/logs/backend.out | tail -3
