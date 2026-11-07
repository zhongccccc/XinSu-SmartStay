#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
sleep 1
cd /opt/zhikong/idreader || exit 1
echo "$PB" | sudo -S -p '' bash -c 'LIBUSB_DEBUG=4 timeout -s KILL 6 /usr/bin/qemu-aarch64-static -L /opt/zhikong/idreader/rootfs /opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/ > /tmp/libusb.log 2>&1'
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
echo "=== libusb 日志（前 40 行）==="
head -40 /tmp/libusb.log
echo "=== 错误/失败 ==="
grep -iE "error|fail|denied|no such|not supported" /tmp/libusb.log | head -15
