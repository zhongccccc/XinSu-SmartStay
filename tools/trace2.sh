#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
sleep 1
cd /opt/zhikong/idreader || exit 1
echo "$PB" | sudo -S -p '' bash -c 'timeout -s KILL 6 strace -f -e trace=%file -o /tmp/tr2.txt /usr/bin/qemu-aarch64-static -L /opt/zhikong/idreader/rootfs /opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/ > /tmp/ir2.out 2>&1'
echo "$PB" | sudo -S -p '' pkill -f "id_reader" 2>/dev/null
echo "lines: $(wc -l < /tmp/tr2.txt)"
echo "=== /dev 打开 ==="
grep -o '"/dev/[^"]*"' /tmp/tr2.txt | sort | uniq -c | sort -rn | head -12
echo "=== hidraw 目录下读了什么 ==="
grep -E "hidraw" /tmp/tr2.txt | grep -vE "readlinkat" | head -20
echo "=== usb 设备 ==="
grep -o '"/sys/bus/usb/devices/[^"]*"' /tmp/tr2.txt | sort -u | head -15
