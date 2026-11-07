#!/bin/bash
echo "=== hidraw 相关系统调用 ==="
grep -n "hidraw" /tmp/tr.txt | head -25
echo
echo "=== 我们设备的 usb 节点 ==="
grep -n "002/008\|002/009\|002/010" /tmp/tr.txt | head -10
echo
echo "=== 读取 sysfs 的 usb 设备属性 ==="
grep -o '"/sys/bus/usb/devices/[^"]*"' /tmp/tr.txt | sort -u | head -25
