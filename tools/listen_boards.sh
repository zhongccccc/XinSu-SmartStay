#!/bin/bash
echo "=== CH340 数量 ==="
lsusb | grep -c '1a86:7523'
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 监听 25 秒（看板子有没有自己输出）==="
echo 123456 | sudo -S -p '' timeout 40 python3 - <<'PY'
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
        print("  %s open 失败: %s" % (p, e))
bufs = {p: b"" for p in fds}
end = time.time() + 25
while time.time() < end:
    rl, _, _ = select.select(list(fds.values()), [], [], 0.2)
    for fd in rl:
        name = [k for k, v in fds.items() if v == fd][0]
        try:
            bufs[name] += os.read(fd, 8192)
        except BlockingIOError:
            pass
for fd in fds.values():
    os.close(fd)
for p, b in bufs.items():
    txt = b.decode('utf-8', 'ignore').strip()
    lines = [l.strip() for l in txt.splitlines() if l.strip()][:5]
    print("  %-14s %d 字节" % (p, len(b)))
    for l in lines:
        print("       |", l[:90])
PY
