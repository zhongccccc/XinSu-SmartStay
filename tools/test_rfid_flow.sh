#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=%-6s guest=%s room=%s card=%s' % (d['step'], d.get('guest'), (d.get('room') or {}).get('no'), d.get('card_uid')))"; }

echo "$PB" | sudo -S -p '' pkill -f rfid_poll.py 2>/dev/null
sleep 1
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 1
echo "=== rfid 状态 ==="
curl -s -m 6 $B/api/health | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('rfid'));print(d.get('idcard'))"

echo
echo "=== 走流程到「房卡」步骤 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.6; st
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6; st
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5; st
curl -s -X POST $B/api/room/8801 > /dev/null; sleep 0.5; st
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay > /dev/null; sleep 0.5; st
echo "--- 等 RFID 自动读到卡（最多 5 秒）---"
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 0.5
  s=$(curl -s -m 3 $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])")
  [ "$s" = "issue" ] && { echo "已进入 issue"; break; }
done
st
echo "--- 下发门锁 ---"
curl -s -X POST $B/api/issue > /dev/null
st
curl -s -m 4 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('开门码:', d.get('lock_code'), '订单:', d.get('order_id'))"
echo "--- RFID 日志 ---"
grep -E "\[rfid\]" /opt/zhikong/logs/backend.out | tail -4
