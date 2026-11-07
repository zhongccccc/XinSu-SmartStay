#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
sleep 1
cd /opt/zhikong/idreader || exit 1
echo "$PB" | sudo -S -p '' bash -c 'timeout -s KILL 6 strace -f -e trace=ioctl,openat -o /tmp/tr3.txt /usr/bin/qemu-aarch64-static -L /opt/zhikong/idreader/rootfs /opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/ > /dev/null 2>&1'
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
echo "=== 打开 usb 设备节点 ==="
grep -E "bus/usb/002/(008|009|010)" /tmp/tr3.txt | head -5
echo "=== USBDEVFS ioctl（0x80.. 0x55..）==="
grep -oE "ioctl\([0-9]+, [A-Z_0-9x]+, " /tmp/tr3.txt | sort | uniq -c | sort -rn | head -15
echo "=== 所有 ioctl 命令号 ==="
grep -oE "ioctl\([0-9]+, 0x[0-9a-f]+" /tmp/tr3.txt | awk '{print $2}' | sort | uniq -c | sort -rn | head -15
echo "=== ENOTTY / EINVAL 次数 ==="
grep -cE "ENOTTY" /tmp/tr3.txt; grep -cE "EINVAL" /tmp/tr3.txt
