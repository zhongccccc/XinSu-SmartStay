#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
echo "$PB" | sudo -S -p '' timeout 160 python3 /tmp/ln.py > /tmp/learn.log 2>&1
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
echo "=== 学习结果 ==="
cat /tmp/learn.log
