#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
echo "=== 执行 zk diag（约 10 秒）==="
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
os.write(fd, b"zk diag\r")
buf=b""
end=time.time()+22
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
    if b"DIAG|DONE" in buf:
        time.sleep(0.5)
        break
os.close(fd)
for line in buf.decode("utf-8","ignore").splitlines():
    s=line.strip()
    if "ZK|DIAG" in s or "ZK|ACK|DIAG" in s:
        print("  ", s[:110])
PY
echo
echo "=== 恢复后台 ==="
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
systemctl is-active zhikong-backend
