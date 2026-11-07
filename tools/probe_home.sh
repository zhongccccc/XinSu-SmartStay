#!/bin/bash
echo "=== 串口 ==="
ls -l /dev/ttyUSB* 2>/dev/null
echo
echo "=== USB 设备 ==="
lsusb | grep -i '1a86\|ch34\|serial' || lsusb | tail -8
echo
echo "=== 逐口探测（谁在跑 zk 协议 / 谁有输出）==="
echo 123456 | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2 /dev/ttyUSB3; do
  [ -e "$p" ] || continue
  echo "--- $p ---"
  echo 123456 | sudo -S -p '' timeout 5 python3 - "$p" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0]=a[1]=0
a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS)
a[3]=0
a[4]=a[5]=termios.B115200
a[6][termios.VMIN]=0
a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
time.sleep(0.2)
buf=b""
end=time.time()+2.0
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.15)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.write(fd, b"\r\nzk ping\r\n")
end=time.time()+2.0
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.15)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.close(fd)
txt=buf.decode("utf-8","ignore").strip()
print("  收到 %d 字节" % len(buf))
for line in txt.splitlines()[:6]:
    s=line.strip()
    if s: print("  |", s[:90])
PY
done
echo 123456 | sudo -S -p '' systemctl start zhikong-backend
