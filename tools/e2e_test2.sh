#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 等后端就绪 ==="
for i in $(seq 1 40); do
  if curl -s -m 1 $B/api/health > /dev/null 2>&1; then echo "  就绪（${i}）"; break; fi
  sleep 1
done

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
echo "=== 办入住（房卡步骤直接给卡号，不等 45 秒）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8806"}' $B/api/card > /dev/null
sleep 8

curl -s $B/api/state > /tmp/e2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/e2.json'))
print("  step=%s 码=%s 卡=%s" % (d.get('step'), d.get('lock_code'), d.get('card_uid')))
open('/tmp/code.txt','w').write(d.get('lock_code') or '')
PY
CODE=$(cat /tmp/code.txt)

if [ -z "$CODE" ]; then echo "!! 没有拿到开门码"; exit 1; fi
echo
echo "=== 在板子上校验 $CODE ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -6
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
