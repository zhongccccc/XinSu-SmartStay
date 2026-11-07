#!/bin/bash
PB=123456
echo "=== 最近的 USB 事件 ==="
echo "$PB" | sudo -S -p '' dmesg 2>/dev/null | grep -iE "ch341|ttyUSB|usb .*new" | tail -8

for dev in /dev/ttyUSB0 /dev/ttyUSB1; do
  echo
  echo "================ $dev ================"
  echo "$PB" | sudo -S -p '' python3 /tmp/sp.py "$dev" 115200 3
  echo "--- 发 ping ---"
  echo "$PB" | sudo -S -p '' python3 - "$dev" <<'PY'
import sys
sys.path.insert(0, '/opt/zhikong/app')
from backend.devices.lock_board import BoardLock
lk = BoardLock(sys.argv[1], log=lambda *a: None)
ok, detail = lk.ping(2.5)
print("  ping:", ok, detail)
lk.close()
PY
done
