#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
show() { curl -s $B/api/home | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('   >>> light=%s fan=%s' %(d['light'],d['fan']))"; }

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8802 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8802"}' $B/api/card > /dev/null
sleep 6
echo "入住后:"; show

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "开门码=$CODE"
echo "凭码退房:"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/checkout | python3 -c "import sys,json;d=json.load(sys.stdin);print('   ', d.get('ok'), d.get('msg'), d.get('room'))"
sleep 3
echo "退房后:"; show
echo "审计:"
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for k, p in c.execute("SELECT kind,payload FROM audit WHERE kind='room_mode' ORDER BY id DESC LIMIT 3"):
    print("   ", k, p)
c.close()
PY
