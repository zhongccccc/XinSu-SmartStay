#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 入住流程 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.4
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 4
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s lock_code=%s' % (d['step'], d.get('lock_code')))"

echo
echo "=== 门锁板收到的指令（模拟器侧）==="
grep -E '^  <-' /tmp/sim.log | tail -4

echo
echo "=== 板子上报的事件是否进了审计 ==="
curl -s $B/api/audit > /tmp/a.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/a.json'))
n = 0
for a in d['items']:
    if a['kind'] in ('lock_issue', 'lock_event', 'lock_open'):
        print("  %-11s %s" % (a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:70]))
        n += 1
        if n >= 5:
            break
PY
