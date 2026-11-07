#!/bin/bash
# 测一次完整开门 → 6 秒自动上锁 的循环
# 用法: sudo bash /opt/zhikong/tools/lock_test.sh
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
  echo "!! 找不到门锁板"
  exit 1
fi
echo "端口: $PORT"
python3 - "$PORT" <<'PY'
import os, select, sys, termios, time
port = sys.argv[1]
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
os.write(fd, b"zk open 8808\r")
print("已发送开锁，等 6 秒自动上锁…")
time.sleep(9)
print("完成")
os.close(fd)
PY
