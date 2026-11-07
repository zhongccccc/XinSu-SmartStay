#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -9 -f 'python3 /tmp/' 2>/dev/null
sleep 1
echo "$PB" | sudo -S -p '' timeout 40 python3 - <<'PY'
import glob, os, select, termios, time

def rd(fd, sec):
    buf=b""
    end=time.time()+sec
    while time.time()<end:
        r,_,_=select.select([fd],[],[],0.2)
        if r:
            try: buf+=os.read(fd,8192)
            except BlockingIOError: pass
    return buf

for p in sorted(glob.glob('/dev/ttyUSB*')):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        print("%-16s open fail: %s" % (p, e)); continue
    a = termios.tcgetattr(fd)
    a[0]=a[1]=0
    a[2]=(a[2]&~termios.CSIZE)|termios.CS8
    a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS)
    a[3]=0
    a[4]=a[5]=termios.B115200
    a[6][termios.VMIN]=0
    a[6][termios.VTIME]=0
    termios.tcsetattr(fd, termios.TCSANOW, a)

    idle = rd(fd, 1.5)
    os.write(fd, b"\r\nzk ping\r\n")
    zk = rd(fd, 1.5)
    os.write(fd, b"zh ping\r\n")
    zh = rd(fd, 1.5)
    os.close(fd)

    tag = []
    if b"ZK|ACK|PING" in zk: tag.append("LOCK")
    if b"ZH|ACK|PING" in zh: tag.append("HOME")
    txt = (idle + zk + zh).decode("utf-8","ignore")
    print("%-16s idle=%d zk=%d zh=%d %s" % (p, len(idle), len(zk), len(zh), ",".join(tag) or "-"))
    for line in [l.strip() for l in txt.splitlines() if l.strip()][:5]:
        print("     |", line[:90])
PY
