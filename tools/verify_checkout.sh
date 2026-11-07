#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

echo "=== 1. 给板子写一个已知码 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend; sleep 1
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import os, select, termios, time
fd = os.open("/dev/ttyUSB2", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
    while os.read(fd,4096): pass
except BlockingIOError: pass
os.write(fd, b"zk issue 8801 111111 CARD01 60\r")
time.sleep(0.8)
buf=b""
end=time.time()+1.2
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
for l in buf.decode("utf-8","ignore").splitlines():
    if "ISSUE" in l: print("  ", l.strip()[:60])
os.close(fd)
PY
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6

echo "=== 2. 校验 111111（应通过）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"111111"}' $B/api/lock/code
echo
sleep 7

echo "=== 3. 调 /api/checkout room=8801 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"room":"8801"}' $B/api/checkout > /dev/null
sleep 2

echo "=== 4. 再校验 111111（应被拒）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"111111"}' $B/api/lock/code
echo
echo
echo "=== 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -6
