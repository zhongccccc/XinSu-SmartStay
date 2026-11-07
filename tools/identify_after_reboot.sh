#!/bin/bash
PB=123456
echo "=== 当前串口 ==="
ls /dev/ttyUSB* 2>/dev/null

echo
echo "=== 单片机在说什么（每口 8 秒）==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' timeout 40 python3 - <<'PY'
import glob, os, select, termios, time
fds = {}
for p in sorted(glob.glob('/dev/ttyUSB*')):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        a = termios.tcgetattr(fd)
        a[0]=a[1]=0; a[2]=(a[2]&~termios.CSIZE)|termios.CS8
        a[2]&=~(termios.PARENB|termios.CSTOPB|termios.CRTSCTS); a[3]=0
        a[4]=a[5]=termios.B115200; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
        termios.tcsetattr(fd, termios.TCSANOW, a)
        fds[p] = fd
    except Exception as e:
        print("  %s 打开失败: %s" % (p, e))
bufs = {p: b"" for p in fds}
end = time.time() + 8
while time.time() < end:
    rl, _, _ = select.select(list(fds.values()), [], [], 0.2)
    for fd in rl:
        name = [k for k, v in fds.items() if v == fd][0]
        try: bufs[name] += os.read(fd, 2048)
        except BlockingIOError: pass
for fd in fds.values(): os.close(fd)
for p, b in bufs.items():
    txt = b.decode("utf-8", "ignore")
    hint = ""
    if "alive" in txt or "ZH|" in txt: hint = "<= 家居板"
    elif "ZK|" in txt: hint = "<= 门锁板"
    print("  %-14s %4d 字节 %s" % (p, len(b), hint))
    if b:
        print("       ", "".join(c if 32 <= ord(c) < 127 else "." for c in txt[:120]))
PY
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 18

echo
echo "=== 后端状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq6.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq6.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'), hm.get('firmware'))
PY
