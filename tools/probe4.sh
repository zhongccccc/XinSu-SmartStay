#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -9 -f 'python3 /tmp/' 2>/dev/null
sleep 2
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB3; do
  [ -e "$p" ] || continue
  echo "--- $p ---"
  echo "$PB" | sudo -S -p '' timeout 7 python3 - "$p" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
try:
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception as e:
    print("  open fail:", e); raise SystemExit
a = termios.tcgetattr(fd)
a[0]=a[1]=0
a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS)
a[3]=0
a[4]=a[5]=termios.B115200
a[6][termios.VMIN]=0
a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
def rd(sec):
    buf=b""
    end=time.time()+sec
    while time.time()<end:
        r,_,_=select.select([fd],[],[],0.2)
        if r:
            try: buf+=os.read(fd,4096)
            except BlockingIOError: pass
    return buf
buf = rd(2.0)
os.write(fd, b"\r\nzh ping\r\n")
buf += rd(2.0)
os.write(fd, b"zk ping\r\n")
buf += rd(2.0)
os.close(fd)
txt=buf.decode("utf-8","ignore").strip()
print("  %d bytes" % len(buf))
for l in txt.splitlines()[:10]:
    s=l.strip()
    if s: print("  |", s[:95])
PY
done
