#!/bin/bash
PB=123456
echo "=== 当前 CH340 与串口 ==="
lsusb | grep -i '1a86:7523' | nl
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 开始监听 USB 事件 50 秒（现在请拔插智能家居板）==="
echo "$PB" | sudo -S -p '' timeout 50 dmesg -w 2>/dev/null | grep --line-buffered -iE 'ch341|ttyUSB|usb 2-|disconnect' | head -40
echo
echo "=== 50 秒后 ==="
lsusb | grep -i '1a86:7523' | nl
ls /dev/ttyUSB* 2>/dev/null
