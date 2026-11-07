#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2; do
  [ -e "$p" ] || continue
  echo "--- $p ---"
  echo "$PB" | sudo -S -p '' timeout 8 python3 /tmp/cb.py "$p" 5 2>&1 | tail -4
done
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
