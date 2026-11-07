#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "=== 端口识别 ==="
echo "$PB" | sudo -S -p '' timeout 90 python3 /tmp/ip.py
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
