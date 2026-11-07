#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 1

PORT=""
for p in /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyUSB2 /dev/ttyUSB3; do
  [ -e "$p" ] || continue
  OUT=$(echo "$PB" | sudo -S -p '' python3 - "$p" <<'PY'
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
    while os.read(fd,4096): pass
except BlockingIOError: pass
os.write(fd, b"zk ping\r")
buf=b""
end=time.time()+2.5
while time.time()<end:
    r,_,_=select.select([fd],[],[],0.2)
    if r:
        try: buf+=os.read(fd,4096)
        except BlockingIOError: pass
os.close(fd)
d=buf.decode("utf-8","ignore")
if "ZK|ACK|PING" in d:
    print(d.strip().splitlines()[0][:80])
    raise SystemExit(0)
raise SystemExit(1)
PY
)
  if [ -n "$OUT" ]; then
    echo "板子: $p  $OUT"
    PORT="$p"
    break
  fi
done

if [ -z "$PORT" ]; then
  echo "!! 没找到板子"
  echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
  exit 1
fi

python3 - "$PORT" <<'PY'
import json, sys
p='/opt/zhikong/etc/config.json'
d=json.load(open(p))
d['devices']['lock'].update({"transport":"board","port":sys.argv[1],"baud":115200})
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("配置端口:", sys.argv[1])
PY

echo "$PB" | sudo -S -p '' python3 - "$PORT" <<'PY'
import os, select, sys, termios, time
p = sys.argv[1]
fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
    if "ISSUE" in line: print("下发:", line.strip()[:70])
os.close(fd)
PY

echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "$PB" | sudo -S -p '' systemctl is-active zhikong-backend
