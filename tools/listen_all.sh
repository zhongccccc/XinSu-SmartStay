#!/bin/bash
echo "=== 串口列表 ==="
ls /dev/ttyUSB* 2>/dev/null
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2 /dev/ttyUSB3; do
  [ -e "$p" ] || continue
  echo
  echo "================ $p ================"
  echo 123456 | sudo -S -p '' timeout 9 python3 /tmp/cb.py "$p" 6 2>&1 | head -14
done
