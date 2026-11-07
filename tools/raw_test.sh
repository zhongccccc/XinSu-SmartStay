#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
echo "=== 现在开始采样，约 12 秒，请按住键盘上的「1」 ==="
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

for round in range(3):
    os.write(fd, b"zk raw\r")
    time.sleep(2.2)
    buf=b""
    end=time.time()+0.5
    while time.time()<end:
        r,_,_=select.select([fd],[],[],0.2)
        if r:
            try: buf+=os.read(fd,4096)
            except BlockingIOError: pass
    vals=[]
    for line in buf.decode("utf-8","ignore").splitlines():
        if "ZK|RAW|" in line:
            vals.append(line.strip().split("|")[-1])
    print("  第%d轮:" % (round+1), " ".join(vals) if vals else "(无数据)")
    time.sleep(1.0)
os.close(fd)
PY
echo
echo "=== 恢复后台 ==="
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 5
systemctl is-active zhikong-backend
