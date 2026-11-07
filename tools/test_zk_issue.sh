#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /tmp/zks.py "zk ping" "zk issue 8808 135790 - 60" "zk code 135790" "zk code 999999"
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
echo "后端: $(systemctl is-active zhikong-backend)"
