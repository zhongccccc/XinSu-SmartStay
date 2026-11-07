#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
cd /opt/zhikong/app
python3 -m py_compile backend/main.py && echo "COMPILE_OK"

echo "=== 清空历史订单 ==="
cat > /tmp/cl9.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("  清理:", cur.rowcount)
c.commit(); c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/cl9.py

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 30

echo "=== 认领结果 ==="
grep -a '\[port\]' /opt/zhikong/logs/backend.log | tail -4

echo
echo "=== 跑一次入住 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1.5
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.5
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8806"}' $B/api/card > /dev/null
sleep 8
curl -s $B/api/state > /tmp/ok.json
CODE=$(python3 -c "
import json
d=json.load(open('/tmp/ok.json'))
print(d.get('lock_code') or '')
")
python3 - <<'PY'
import json
d = json.load(open('/tmp/ok.json'))
print("  step=%s 码=%s 卡=%s" % (d.get('step'), d.get('lock_code'), d.get('card_uid')))
PY

echo
echo "=== 板上校验这个码 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -6
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
