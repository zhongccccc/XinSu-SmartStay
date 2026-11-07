#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
step() { curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('   step=%s code=%s msg=%s' % (d.get('step'), d.get('lock_code'), (d.get('msg') or '')[:40]))"; }

python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='mock'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 8

echo "1 cancel";     curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8; step
echo "2 start";      curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5; step
echo "3 idcard";     curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5; step
echo "4 face";       curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.4; step
echo "5 room 8803";  curl -s -X POST $B/api/room/8803 > /dev/null; sleep 0.4; step
echo "6 pay";        curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.4; step
echo "7 card";       curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8803"}' $B/api/card > /dev/null; sleep 6; step
echo "8 home";       curl -s $B/api/home | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('   light=%s fan=%s' %(d['light'],d['fan']))"
echo "9 audit";      curl -s -X POST $B/api/cancel > /dev/null
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for k, p in c.execute("SELECT kind,payload FROM audit ORDER BY id DESC LIMIT 6"):
    print("   ", k, str(p)[:90])
c.close()
PY
