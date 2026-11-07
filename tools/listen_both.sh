#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
for p in /dev/ttyUSB0 /dev/ttyUSB1; do
  [ -e "$p" ] || continue
  echo "--- $p ---"
  echo "$PB" | sudo -S -p '' timeout 6 python3 - "$p" <<'PY'
import os, select, sys, termios, time
dev = sys.argv[1]
fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0]=a[1]=0
a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS)
a[3]=0
a[4]=a[5]=termios.B115200
a[6][termios.VMIN]=0
a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
buf=b""
end=time.time()+4
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.close(fd)
txt = buf.decode("utf-8","ignore").strip()
print("  收到 %d 字节" % len(buf))
if txt:
    for line in txt.splitlines()[:4]:
        print("  |", line.strip()[:80])
PY
done
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
echo
echo "=== 最近的 USB 事件 ==="
echo "$PB" | sudo -S -p '' dmesg 2>/dev/null | grep -iE 'ch341|ttyUSB' | tail -6
