#!/bin/bash
PB=123456
echo "=== 手册里的波特率/地址说明 ==="
python3 /tmp/ep.py /tmp/rfid_manual.pdf /tmp/rfid_manual.txt > /dev/null 2>&1 || cp /e/zhikong 2>/dev/null
if [ -f /tmp/rfid_manual.txt ]; then
  grep -nE "波特率|9600|115200|地址|0x20|通讯|串口" /tmp/rfid_manual.txt | head -20
else
  echo "manual not on board"
fi

echo
echo "=== 拉起 DTR/RTS 后再读 ==="
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import fcntl, os, select, termios, time
TIOCMBIS = 0x5416
for baud in (termios.B9600, termios.B115200):
    fd = os.open("/dev/ttyUSB0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[4] = a[5] = baud
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB)
    termios.tcsetattr(fd, termios.TCSANOW, a)
    # DTR(0x02) + RTS(0x04)
    for bit in (0x02, 0x04):
        try:
            fcntl.ioctl(fd, TIOCMBIS, bit)
        except Exception as e:
            print("ioctl", hex(bit), e)
    time.sleep(0.3)
    os.write(fd, bytes([0x01,0x08,0xA1,0x20,0x00,0x01,0x00,0x76]))
    buf = b""
    end = time.time() + 1.2
    while time.time() < end:
        r,_,_ = select.select([fd], [], [], 0.1)
        if r:
            buf += os.read(fd, 64)
    print("baud=%d -> %s" % (baud, buf.hex(" ") if buf else "(无应答)"))
    os.close(fd)
PY
