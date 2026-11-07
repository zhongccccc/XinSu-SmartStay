#!/bin/bash
PB=123456
systemctl is-active zhikong-backend > /dev/null || echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 2
# 通过后端接口直接下发（后端已接 ttyUSB2）
curl -s -X POST -H 'Content-Type: application/json' -d '{"pin":"135790"}' http://127.0.0.1:8080/api/lock/code > /tmp/c1.json 2>&1
cat /tmp/c1.json
echo
# 直接用板子命令写入凭证更可靠
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
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
os.write(fd, b"zk issue 8801 135790 CARD01 60\r")
time.sleep(1.0)
buf=b""
end=time.time()+1.2
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
for line in buf.decode("utf-8","ignore").splitlines():
    if "ISSUE" in line: print("板子:", line.strip()[:70])
os.close(fd)
PY
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
echo "$PB" | sudo -S -p '' systemctl is-active zhikong-backend
