#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 重新下发在住订单的凭证 ==="
curl -s -X POST $B/api/lock/resync
echo

sleep 2
echo "=== 校验 ==="
CODE=$(curl -s $B/api/state | python3 -c "
import sys, json
d = json.load(sys.stdin)
ins = d.get('inhouse') or []
print(ins[0].get('lock_code') if ins else '')
")
echo "  开门码 $CODE"
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -8
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
