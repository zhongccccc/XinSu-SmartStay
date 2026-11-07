#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 设备 ==="
curl -s $B/api/health > /tmp/e1.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/e1.json'))
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), lk.get('online'), "mock=", lk.get('mock'), lk.get('firmware'))
print("  家居板:", hm.get('port'), hm.get('online'))
print("  读卡器:", rf.get('port'), rf.get('online'))
PY

echo
echo "=== 办入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8806"}' $B/api/card > /dev/null
sleep 8

curl -s $B/api/state > /tmp/e2.json
CODE=$(python3 -c "
import json
d = json.load(open('/tmp/e2.json'))
print(d.get('lock_code') or '')
print('  step=%s 卡=%s' % (d.get('step'), d.get('card_uid')), file=__import__('sys').stderr)
")
echo "  开门码: $CODE"

if [ -z "$CODE" ]; then echo "!! 没拿到码"; exit 1; fi

echo
echo "=== 门锁板校验 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -6
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
