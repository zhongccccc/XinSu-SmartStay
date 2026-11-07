#!/bin/bash
# 调整门锁开/关时长（毫秒）
# 用法: sudo bash /opt/zhikong/tools/lock_tune.sh 400 600
set -e
OPEN_MS="${1:-400}"
LOCK_MS="${2:-600}"
FIND=""

PORT=""
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2 /dev/ttyUSB3; do
  [ -e "$p" ] || continue
  OUT=$(python3 - "$p" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
try:
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception:
    raise SystemExit(1)
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
try:
    while os.read(fd,8192): pass
except BlockingIOError: pass
os.write(fd, b"zk ping\r")
buf=b""
end=time.time()+1.8
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.15)
    if r:
        try: buf+=os.read(fd,8192)
        except BlockingIOError: pass
os.close(fd)
print("OK" if b"ZK|ACK|PING" in buf else "")
PY
)
  if [ -n "$OUT" ]; then PORT="$p"; break; fi
done

if [ -z "$PORT" ]; then
  echo "!! 找不到门锁板（检查 USB 是否插在 K1 上、OLED 是否亮）"
  exit 1
fi

python3 - "$PORT" "$OPEN_MS" "$LOCK_MS" <<'PY'
import os, select, sys, termios, time
port, o, l = sys.argv[1], sys.argv[2], sys.argv[3]
fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
try:
    while os.read(fd,8192): pass
except BlockingIOError: pass
os.write(fd, ("zk pt %s %s\r" % (o, l)).encode())
buf=b""
end=time.time()+1.2
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.15)
    if r:
        try: buf+=os.read(fd,8192)
        except BlockingIOError: pass
os.close(fd)
for line in buf.decode("utf-8","ignore").splitlines():
    if "PT|OK" in line:
        print("已设置:", line.strip())
PY
