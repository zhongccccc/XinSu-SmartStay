#!/bin/bash
PB=123456
echo "监听 ttyUSB1 90 秒，按 RESET 后应看到启动日志…"
echo "$PB" | sudo -S -p '' python3 - /dev/ttyUSB1 90 <<'PY'
import os, select, sys, termios, time
dev, secs = sys.argv[1], float(sys.argv[2])
fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = termios.B115200
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
buf = b""
end = time.time() + secs
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.3)
    if r:
        try:
            d = os.read(fd, 2048)
        except BlockingIOError:
            continue
        if d:
            buf += d
            for line in d.decode("utf-8", "ignore").splitlines():
                if line.strip():
                    print("  | " + line.strip()[:110], flush=True)
os.close(fd)
print("共收到 %d 字节" % len(buf), flush=True)
PY
