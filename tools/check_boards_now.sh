#!/bin/bash
PB=123456
echo "=== 谁在吃 CPU ==="
ps -eo pcpu,pmem,comm --sort=-pcpu 2>/dev/null | head -6

echo
echo "=== 各串口在说什么（8 秒）==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' timeout 30 python3 /opt/zhikong/tools/raw_listen.py 2>&1 | head -20
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 4
echo "后端: $(systemctl is-active zhikong-backend)"
