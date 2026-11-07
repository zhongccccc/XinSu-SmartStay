#!/bin/bash
echo "=== ttyUSB ==="
ls -l /dev/ttyUSB* 2>/dev/null || echo "无 ttyUSB 设备"
echo "=== 占用进程 ==="
echo 123456 | sudo -S -p '' fuser -v /dev/ttyUSB0 2>&1 | head -5
echo "=== 后端 rfid 日志 ==="
grep -E "\[rfid\]" /opt/zhikong/logs/backend.out | tail -6
echo "=== 手动打开测试 ==="
python3 - <<'PY'
import os, termios
try:
    fd = os.open("/dev/ttyUSB0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    print("open OK, fd =", fd)
    os.close(fd)
except OSError as e:
    print("open FAIL:", e)
PY
echo "=== dmesg 最近 USB ==="
echo 123456 | sudo -S -p '' dmesg 2>/dev/null | tail -6
