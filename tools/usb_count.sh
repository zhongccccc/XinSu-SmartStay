#!/bin/bash
PB=123456
echo "=== CH340 设备 ==="
lsusb | grep -i '1a86:7523' | nl
echo
echo "=== 实际串口 ==="
ls -l /dev/ttyUSB* 2>/dev/null
echo
echo "=== ch341 驱动日志（最近 15 条）==="
echo "$PB" | sudo -S -p '' dmesg 2>/dev/null | grep -i 'ch341\|ttyUSB' | tail -15
echo
echo "=== 所有 USB 串口类设备 ==="
ls /sys/bus/usb-serial/devices/ 2>/dev/null
