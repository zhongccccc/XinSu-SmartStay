#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 门锁状态 ==="
curl -s $B/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
print("  lock:", d.get('lock'))
PY

echo
echo "=== 完整入住流程 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s code=%s' % (d['step'], d.get('lock_code')))"

echo
echo "=== 审计（门锁相关）==="
curl -s $B/api/audit > /tmp/a.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/a.json'))
n = 0
for a in d['items']:
    if a['kind'].startswith('lock'):
        print("  %-12s %s" % (a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:70]))
        n += 1
        if n >= 6:
            break
PY

echo
echo "=== 后端日志里的门锁行 ==="
grep -a "\[lock\]" /opt/zhikong/logs/backend.out | tail -5
