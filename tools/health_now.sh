#!/bin/bash
PB=123456
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 板卡应答 ==="
for p in /dev/ttyUSB*; do
  [ -e "$p" ] || continue
  echo 123456 | sudo -S -p '' timeout 6 python3 - "$p" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
try:
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception as e:
    print("  %-14s open 失败" % p); raise SystemExit
a = termios.tcgetattr(fd)
a[0]=a[1]=0; a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS); a[3]=0
a[4]=a[5]=termios.B115200; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
def rd(sec):
    b=b""; end=time.time()+sec
    while time.time()<end:
        r,_,_=select.select([fd],[],[],0.15)
        if r:
            try: b+=os.read(fd,8192)
            except BlockingIOError: pass
    return b
rd(0.8)
os.write(fd, b"zk ping\r"); zk = rd(1.6)
os.write(fd, b"zh ping\r"); zh = rd(1.6)
os.close(fd)
tag = []
if b"ZK|ACK|PING" in zk: tag.append("门锁板")
if b"ZH|ACK|PING" in zh: tag.append("家居板")
txt = (zk + zh).decode("utf-8","ignore")
ver = ""
for line in txt.splitlines():
    if "|PING|OK|" in line:
        ver = line.split("|PING|OK|")[1].split("|")[0]
print("  %-14s %s %s" % (p, ",".join(tag) or "无应答", ver))
PY
done
echo
echo "=== 后端 ==="
systemctl is-active zhikong-backend
curl -s http://127.0.0.1:8080/api/health > /tmp/hh.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hh.json'))
    lk = d.get('lock') or {}
    hm = d.get('home') or {}
    print("  lock :", lk.get('transport'), "online=", lk.get('online'), lk.get('port'))
    print("  home :", hm.get('online'), hm.get('firmware'), hm.get('port'))
    print("  camera:", (d.get('camera') or {}).get('ok'))
except Exception as e:
    print("  health 读取失败:", e)
PY
