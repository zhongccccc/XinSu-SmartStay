#!/bin/bash
PB=123456
echo "=== 各波特率下测试读卡命令 ==="
for b in 9600 19200 38400 57600 115200; do
  echo "--- $b"
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/rfid_read.py /dev/ttyUSB0 $b 2>&1 | grep -E "attempt 1|卡号|状态|checksum" | head -3
done
echo
echo "=== 串口线路状态 ==="
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import termios, os
fd = os.open('/dev/ttyUSB0', os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
attrs = termios.tcgetattr(fd)
print("iflag=%x oflag=%x cflag=%x lflag=%x" % (attrs[0], attrs[1], attrs[2], attrs[3]))
os.close(fd)
PY
