#!/bin/bash
echo "=== camera_json ==="
ls -l /usr/share/camera_json/ 2>/dev/null | head -20
echo
echo "=== cam-test ==="
head -30 /usr/bin/cam-test 2>/dev/null
echo
echo "=== i2c 总线列表 ==="
i2cdetect -l 2>/dev/null
echo
echo "=== 扫描各总线上的 sensor 地址 ==="
for b in /dev/i2c-*; do
  n=${b##*-}
  out=$(i2cdetect -y -r "$n" 2>/dev/null | grep -oE "^(10|1a|20|21|30|36|3c|40|48|6c):" | tr '\n' ' ')
  [ -n "$out" ] && echo "i2c-$n: $out"
done
echo
echo "=== 内核里 camera 相关驱动 ==="
lsmod | grep -iE "ov|imx|gc[0-9]|camera|ccic|isp|cam" | head
echo
echo "=== 设备树里的 sensor ==="
ls /proc/device-tree/ | grep -i -E "cam|sensor|csi" | head
for d in /proc/device-tree/*camera* /proc/device-tree/*cam*; do
  [ -d "$d" ] && echo "--- $d" && ls "$d" | head -10
done 2>/dev/null | head -30
