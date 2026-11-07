#!/bin/bash
echo "=== 用户组 ==="
id -nG shiqi | tr ' ' '\n' | grep -E 'dialout|tty' || echo "  不在 dialout 组"
echo
echo "=== USB CH340 数量 ==="
lsusb | grep -c '1a86:7523'
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 直接探测（不带 sudo）==="
python3 - <<'PY'
import glob, os, select, termios, time

def probe(p):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        return "open 失败: %s" % e
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)

    def rd(sec):
        b = b""
        end = time.time() + sec
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.15)
            if r:
                try:
                    b += os.read(fd, 8192)
                except BlockingIOError:
                    pass
        return b

    rd(0.6)
    os.write(fd, b"zk ping\r")
    zk = rd(1.5)
    os.write(fd, b"zh ping\r")
    zh = rd(1.5)
    os.close(fd)
    tags = []
    if b"ZK|ACK|PING" in zk:
        tags.append("门锁板")
    if b"ZH|ACK|PING" in zh:
        tags.append("家居板")
    ver = ""
    for line in (zk + zh).decode("utf-8", "ignore").splitlines():
        if "|PING|OK|" in line:
            ver = line.split("|PING|OK|")[1].split("|")[0]
    return "%s %s" % (",".join(tags) or "无应答", ver)

for p in sorted(glob.glob("/dev/ttyUSB*")):
    print("  %-14s %s" % (p, probe(p)))
PY
