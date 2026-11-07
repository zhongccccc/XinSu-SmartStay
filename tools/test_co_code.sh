#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='mock'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 7

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8805 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8805"}' $B/api/card > /dev/null
sleep 4

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "本次开门码: $CODE"

echo
echo "--- 用错误码退房 ---"
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"000000"}' $B/api/checkout | head -c 200
echo

echo "--- 用正确码退房 ---"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/checkout | head -c 200
echo

echo "--- 退房后在住订单数 ---"
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d.get('inhouse') or []))"

# 恢复 board
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='board'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("已切回 board")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 6
