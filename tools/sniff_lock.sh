#!/bin/bash
PB=123456
for dev in /dev/ttyUSB1 /dev/ttyUSB0; do
  echo "======================================"
  echo "=== $dev ==="
  for baud in 115200 9600; do
    echo "--- ${baud} 8N1，被动监听 3 秒 ---"
    echo "$PB" | sudo -S -p '' python3 - "$dev" "$baud" <<'PY'
import os, select, sys, termios, time
dev, baud = sys.argv[1], int(sys.argv[2])
SPEED = {9600: termios.B9600, 115200: termios.B115200}[baud]
try:
    fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except OSError as e:
    print("  open fail:", e); raise SystemExit
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = SPEED
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
buf = b""
end = time.time() + 3
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try: buf += os.read(fd, 512)
        except BlockingIOError: pass
os.close(fd)
if not buf:
    print("  (无数据)")
else:
    print("  收到 %d 字节" % len(buf))
    txt = "".join(chr(c) if 32 <= c < 127 or c in (10, 13) else "." for c in buf[:600])
    print("  文本: %r" % txt)
    print("  HEX :", buf[:80].hex(" "))
PY
  done
done
