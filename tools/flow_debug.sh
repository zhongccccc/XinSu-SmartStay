#!/bin/bash
B=http://127.0.0.1:8080
s() { curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print(' step=%-8s msg=%s' % (d.get('step'), (d.get('message') or '')[:50]))"; }

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8; echo -n "cancel:"; s
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5; echo -n "start:"; s
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5; echo -n "idcard:"; s
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5; echo -n "face:"; s
echo -n "room resp: "; curl -s -X POST $B/api/room/8809; echo; sleep 0.5; echo -n "room:"; s
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.5; echo -n "pay:"; s
echo -n "card resp: "; curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8809"}' $B/api/card; echo
sleep 4
echo -n "final:"; s
echo
echo "=== 后端日志尾部 ==="
tail -12 /opt/zhikong/logs/backend.out
