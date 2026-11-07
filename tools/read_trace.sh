#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f "strace -f" 2>/dev/null
echo "trace lines: $(wc -l < /tmp/tr.txt 2>/dev/null || echo none)"
echo "=== /dev 打开 ==="
grep -o '"/dev/[^"]*"' /tmp/tr.txt 2>/dev/null | sort | uniq -c | sort -rn | head -15
echo "=== hid / usb sysfs ==="
grep -o '"/sys/[^"]*"' /tmp/tr.txt 2>/dev/null | grep -iE "hid|usb" | sort -u | head -20
echo "=== 服务 stdout ==="
head -25 /tmp/ir.out 2>/dev/null
