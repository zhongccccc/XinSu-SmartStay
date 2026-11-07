#!/bin/bash
# 门锁板联调：让后端连模拟器，跑一次入住流程
B=http://127.0.0.1:8080
echo "=== 让后端用模拟器作为门锁板 ==="
CONF=/opt/zhikong/etc/config.json
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {}).setdefault('lock', {}).update(
    {"transport": "board", "port": "/tmp/ttyLOCK", "baud": 115200})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("  lock =", d['devices']['lock'])
PY

echo "=== 重启后端 ==="
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 2

echo "=== 门锁状态 ==="
curl -s $B/api/health | python3 -c "import sys,json;print('  ', json.load(sys.stdin).get('lock'))"

echo "=== 跑一遍入住到下发门锁 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.4
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 3
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s code=%s' % (d['step'], d.get('lock_code')))"

echo "=== 门锁板侧收到了什么 ==="
tail -8 /tmp/sim.log
