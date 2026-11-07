#!/bin/bash
PB=123456
echo "=== 趁板子活着，直接下发一个测试凭证 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py \
  "zk ping" \
  "zk issue 8808 135790 - 60" \
  "zk code 135790" \
  "zk code 111111"
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
