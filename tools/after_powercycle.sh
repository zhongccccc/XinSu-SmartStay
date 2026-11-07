#!/bin/bash
PB=123456
echo "=== 等板子启动 ==="
sleep 20
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 14

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h7.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/h7.json'))
except Exception:
    print("  后端未就绪"); raise SystemExit
print("  rfid :", d.get('rfid'))
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY

echo
echo "=== 独占串口测读卡器（10 秒）==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' timeout 25 python3 - <<'PY'
import os, select, termios, time
fd = os.open('/dev/ttyUSB0', os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0]=a[1]=0; a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS); a[3]=0
a[4]=a[5]=termios.B9600; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
cmd = bytes([0x01,0x08,0xA1,0x20,0x20,0x00,0x01,0x00,0x76])
hits = 0
for i in range(30):
    try:
        while os.read(fd, 512): pass
    except BlockingIOError: pass
    os.write(fd, cmd)
    buf = b""
    t = time.time() + 0.3
    while time.time() < t:
        r,_,_ = select.select([fd],[],[],0.05)
        if r:
            try: buf += os.read(fd, 256)
            except BlockingIOError: pass
    if len(buf) >= 3:
        hits += 1
        print("  收到:", buf.hex(" "))
os.close(fd)
print("  响应次数:", hits)
PY
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
