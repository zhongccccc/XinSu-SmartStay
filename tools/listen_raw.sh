#!/bin/bash
PB=123456
echo "=== 暂停后台（释放串口）==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1

echo
echo "=== 监听 ttyUSB2 共 8 秒 ==="
echo "$PB" | sudo -S -p '' timeout 12 python3 /tmp/cb.py /dev/ttyUSB2 8 2>&1 | head -20

echo
echo "=== 恢复后台 ==="
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
systemctl is-active zhikong-backend
