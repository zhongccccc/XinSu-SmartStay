#!/bin/bash
PB=123456
echo "=== 进程 ==="
ps aux | grep -E "qemu-aarch64|id_reader" | grep -v grep | head -5
echo
echo "=== USB 设备节点权限 ==="
ls -l /dev/bus/usb/002/ | grep -E "008|009|010"
echo
echo "=== 服务日志 ==="
find /tmp /var/log /opt/zhikong/idreader /root -maxdepth 3 -name "*.log" -newermt "-20 minutes" 2>/dev/null | head -10
for f in $(find /tmp /var/log /opt/zhikong/idreader -maxdepth 3 -name "*.log" -newermt "-20 minutes" 2>/dev/null | head -3); do
  echo "--- $f"; tail -15 "$f"
done
echo
echo "=== 库里跟 VID/PID、hidraw、tty 有关的信息 ==="
strings /opt/zhikong/idreader/lib/libsdtapi.so | grep -iE "vid|pid|hidraw|/dev/|tty|usb|protocol" | head -25
echo
echo "=== id_reader 里的 config 关键字 ==="
strings /opt/zhikong/idreader/bin/id_reader | grep -iE "protocol|hidraw|tty|/dev/|usb_|vid|pid|serial" | head -30
