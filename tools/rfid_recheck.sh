#!/bin/bash
pb() { python3 - <<'PY'
import json
d = json.load(open('/tmp/hr.json'))
print(d.get('rfid'))
PY
}
curl -s http://127.0.0.1:8080/api/health > /tmp/hr.json 2>/dev/null
echo "=== 设备 ==="
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hr.json'))
except Exception as e:
    print("  health 读不到:", e); raise SystemExit
print("  rfid :", d.get('rfid'))
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
echo
echo "=== 独占 ttyUSB0 测读卡器（15 秒，请把卡放上）==="
echo 123456 | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo 123456 | sudo -S -p '' timeout 22 python3 - <<'PY'
import os, select, termios, time
try:
    fd = os.open('/dev/ttyUSB0', os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception as e:
    print("  open 失败:", e); raise SystemExit
a = termios.tcgetattr(fd)
a[0]=a[1]=0; a[2]=(a[2]&~termios.CSIZE)|termios.CS8
a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS); a[3]=0
a[4]=a[5]=termios.B9600; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
termios.tcsetattr(fd, termios.TCSANOW, a)
cmd = bytes([0x01,0x08,0xA1,0x20,0x20,0x00,0x01,0x00,0x76])
hits = 0
for i in range(40):
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
        if hits <= 5: print("  收到:", buf.hex(" "))
os.close(fd)
print("  响应次数:", hits)
PY
echo 123456 | sudo -S -p '' systemctl start zhikong-backend
sleep 8
echo "后端: $(systemctl is-active zhikong-backend)"
