#!/bin/bash
PB=123456
ROOT=/opt/zhikong/idreader/rootfs
APP=/opt/zhikong/idreader

echo "=== 1. 清理旧进程 ==="
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
sleep 1

echo "=== 2. 设备现状 ==="
ls -l /dev/hidraw* 2>/dev/null
for h in /dev/hidraw*; do
  n=$(grep HID_NAME /sys/class/hidraw/${h##*/}/device/uevent 2>/dev/null | cut -d= -f2)
  echo "  $h -> $n"
done

echo "=== 3. strace 跑服务 8 秒 ==="
cd $APP
echo "$PB" | sudo -S -p '' bash -c "timeout -s KILL 8 strace -f -e trace=openat,ioctl,read -o /tmp/tr5.txt \
  /usr/bin/qemu-aarch64-static -L $ROOT $APP/bin/id_reader -a -p $APP/cfg/ > /tmp/ir5.out 2>&1"
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
echo "trace 行数: $(wc -l < /tmp/tr5.txt 2>/dev/null)"

echo "=== 4. 它打开过哪些设备节点 ==="
grep -oE '"/dev/[^"]*"' /tmp/tr5.txt 2>/dev/null | sort | uniq -c | sort -rn | head -12

echo "=== 5. 有没有碰 hidraw ==="
grep -i "hidraw" /tmp/tr5.txt 2>/dev/null | head -8

echo "=== 6. ioctl 调用统计（前 10）==="
grep -oE "ioctl\([0-9]+, 0x[0-9a-f]+" /tmp/tr5.txt 2>/dev/null | awk '{print $2}' | sort | uniq -c | sort -rn | head -10

echo "=== 7. 服务输出 ==="
head -12 /tmp/ir5.out 2>/dev/null
