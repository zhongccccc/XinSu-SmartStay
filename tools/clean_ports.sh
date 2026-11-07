#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f 'hbc.py' 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f 'ca.py' 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f 'lst.py' 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f 'probe' 2>/dev/null
sleep 2
echo "=== 串口 ==="
ls -l /dev/ttyUSB* 2>/dev/null
echo
echo "=== 占用检查 ==="
echo "$PB" | sudo -S -p '' fuser -v /dev/ttyUSB0 /dev/ttyUSB1 2>&1 | head -8
echo
echo "=== 各口快速试探 ==="
for p in /dev/ttyUSB0 /dev/ttyUSB1; do
  [ -e "$p" ] || continue
  echo "--- $p ---"
  echo "$PB" | sudo -S -p '' timeout 5 python3 - "$p" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
try:
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception as e:
    print("  open 失败:", e); raise SystemExit
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
end=time.time()+3
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.write(fd, b"\r\nzh ping\r\n")
end=time.time()+1.5
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.close(fd)
txt=buf.decode("utf-8","ignore").strip()
print("  %d 字节" % len(buf))
for l in txt.splitlines()[:6]:
    s=l.strip()
    if s: print("  |", s[:90])
PY
done
