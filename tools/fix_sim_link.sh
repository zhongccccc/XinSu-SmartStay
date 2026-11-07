#!/bin/bash
cd /opt/zhikong/app
pkill -f lock_board_sim 2>/dev/null
sleep 0.6
mkdir -p /opt/zhikong/run
setsid nohup python3 tools/lock_board_sim.py --link /opt/zhikong/run/ttyLOCK > /tmp/sim.log 2>&1 < /dev/null &
sleep 2
head -2 /tmp/sim.log
ls -l /opt/zhikong/run/ttyLOCK

echo "=== 改配置指向新链接 ==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock']['port'] = '/opt/zhikong/run/ttyLOCK'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("  port =", d['devices']['lock']['port'])
PY

bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -2
sleep 2
echo "=== 门锁状态 ==="
curl -s http://127.0.0.1:8080/api/health | python3 -c "import sys,json;print('  ', json.load(sys.stdin).get('lock'))"
