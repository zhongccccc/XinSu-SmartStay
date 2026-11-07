#!/bin/bash
PB=123456
echo "=== 串口节点 ==="
ls -l /dev/ttyUSB1

echo
echo "=== 被动监听 5 秒（看板子启动日志/回显）==="
echo "$PB" | sudo -S -p '' python3 /tmp/sp.py /dev/ttyUSB1 115200 5 || {
  echo "  没有 /tmp/sp.py，改用内联"
  echo "$PB" | sudo -S -p '' timeout 8 cat /dev/ttyUSB1 | head -c 400 | cat -v
}

echo
echo "=== 主动 ping 一次 ==="
python3 - <<'PY'
import sys, time
sys.path.insert(0, '/opt/zhikong/app')
from backend.devices.lock_board import BoardLock
lk = BoardLock('/dev/ttyUSB1', on_event=lambda t, v: print("  EVENT", t, v))
print("  ping :", lk.ping(3.0))
print("  issue:", lk.issue('8801', '测试', '123456', '-', 60))
print("  status:", lk.status())
lk.close()
PY
