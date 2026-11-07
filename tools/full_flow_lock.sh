#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 临时指向模拟器 ==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock'].update({"transport": "board", "port": "/opt/zhikong/run/ttyLOCK"})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
PY
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -2
sleep 2
curl -s $B/api/health | python3 -c "import sys,json;print('  lock:', json.load(sys.stdin).get('lock'))"

echo
echo "=== 完整入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s code=%s' % (d['step'], d.get('lock_code')))"

echo "=== 板子侧 ==="
grep -E '^  <-' /tmp/sim.log | tail -3

echo "=== 退房（应触发 revoke）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.5
grep -E '^  <-' /tmp/sim.log | tail -2

echo "=== 审计 ==="
curl -s $B/api/audit > /tmp/a.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/a.json'))
n = 0
for a in d['items']:
    if a['kind'].startswith('lock'):
        print("  %-12s %s" % (a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:64]))
        n += 1
        if n >= 5:
            break
PY
