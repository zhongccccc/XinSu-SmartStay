#!/bin/bash
PB=123456
pkill -f "qemu-aarch64-static" 2>/dev/null
sleep 1
echo "$PB" | sudo -S -p '' apt-get install -y strace > /tmp/strace_install.log 2>&1
command -v strace || { echo "no strace"; exit 1; }

cd /opt/zhikong/idreader || exit 1
echo "$PB" | sudo -S -p '' timeout 8 strace -f -e trace=openat,access,stat,newfstatat -o /tmp/tr.txt \
  /usr/bin/qemu-aarch64-static -L /opt/zhikong/idreader/rootfs \
  /opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/ > /tmp/ir.out 2>&1

echo "=== 打开的 /dev 设备 ==="
grep -o '"/dev/[^"]*"' /tmp/tr.txt | sort | uniq -c | sort -rn | head -20
echo
echo "=== 访问的 sys 路径（usb/hid）==="
grep -o '"/sys/[^"]*"' /tmp/tr.txt | grep -iE "hid|usb" | head -15
echo
echo "=== 关心的 vid/pid ==="
grep -o '"/sys/bus/usb/devices/[^"]*"' /tmp/tr.txt | head -10
echo
echo "=== 服务输出 ==="
head -20 /tmp/ir.out
