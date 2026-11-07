#!/bin/bash
PB=123456
CMD="${1:-zh inv 1}"
echo "=== 停后端 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "=== 发送: $CMD ==="
echo "$PB" | sudo -S -p '' python3 /tmp/zs.py "$CMD"
sleep 1
echo "=== 起后端 ==="
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
echo "done"
