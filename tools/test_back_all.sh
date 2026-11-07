#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  -> %-5s guest=%s room=%s card=%s' % (d['step'], d.get('guest'), (d.get('room') or {}).get('no'), d.get('card_uid')))"; }
back() { curl -s -X POST $B/api/back > /dev/null; sleep 0.5; }

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.5
echo "从待机开始逐级前进，再逐级返回："
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5; st
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5; st
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.4; st
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.4; st
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.4; st
echo "--- 逐级返回 ---"
back; st
back; st
back; st
back; st
back; st
back; st
echo "--- 审计（back 记录）---"
curl -s $B/api/audit > /tmp/a.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/a.json'))
for a in d['items'][:8]:
    if a['kind'] == 'back':
        print("  back:", a['payload'])
PY
grim /tmp/back_final.png
