#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

echo "=== 1. 后端接口耗时（连续 5 次入住全流程）==="
for i in $(seq 1 5); do
  T0=$(date +%s.%N)
  curl -s -X POST $B/api/cancel > /dev/null
  curl -s -X POST $B/api/session/start > /dev/null
  curl -s -X POST $B/api/idcard/mock > /dev/null
  curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null
  curl -s -X POST $B/api/room/8801 > /dev/null
  curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"T"}' $B/api/pay > /dev/null
  curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARDX"}' $B/api/card > /dev/null
  T1=$(date +%s.%N)
  echo "  第 $i 次: $(echo "$T1 - $T0" | bc) 秒"
  sleep 1
done

echo
echo "=== 2. 门锁板往返时延（zk ping，5 次）==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend > /dev/null 2>&1
sleep 2
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import os, select, termios, glob, time

def open_port(p):
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd

def read_until(fd, sec):
    buf = b""
    end = time.time() + sec
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                buf += os.read(fd, 512)
            except BlockingIOError:
                pass
            if b"ZK|ACK|PING" in buf:
                return buf, True
    return buf, False

port = None
for p in sorted(glob.glob('/dev/ttyUSB*')):
    try:
        fd = open_port(p)
    except Exception:
        continue
    os.write(fd, b'zk ping\r')
    buf, ok = read_until(fd, 1.5)
    os.close(fd)
    if ok:
        port = p
        break
if not port:
    print("  未找到门锁板")
    raise SystemExit

fd = open_port(port)
times = []
for _ in range(5):
    try:
        while os.read(fd, 512):
            pass
    except BlockingIOError:
        pass
    t0 = time.time()
    os.write(fd, b'zk ping\r')
    buf, ok = read_until(fd, 2.0)
    if ok:
        times.append((time.time() - t0) * 1000)
    time.sleep(0.2)
os.close(fd)
if times:
    print("  端口 %s，5 次往返: %s ms" % (port, ", ".join("%.0f" % t for t in times)))
    print("  平均 %.0f ms，最大 %.0f ms" % (sum(times) / len(times), max(times)))
PY
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend > /dev/null 2>&1
sleep 3
