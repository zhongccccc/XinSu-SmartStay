#!/bin/bash
PB=123456
echo "=== 板子是否应答 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' timeout 40 python3 /opt/zhikong/tools/zk_send.py \
  "zk ping" \
  "zk issue 8808 135790 - 60" \
  "zk code 135790" \
  "zk code 111111" 2>&1 | head -20
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
echo "后端: $(systemctl is-active zhikong-backend)"
