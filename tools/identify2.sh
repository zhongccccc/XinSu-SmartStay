#!/bin/bash
echo "=== 0400:c35a 描述符 ==="
lsusb -v -d 0400:c35a 2>&1 | sed -n '1,55p'
echo
echo "=== hidraw report descriptors ==="
for h in /dev/hidraw2 /dev/hidraw3; do
  echo "--- $h ($(grep HID_NAME /sys/class/hidraw/${h##*/}/device/uevent 2>/dev/null))"
  cat /sys/class/hidraw/${h##*/}/device/report_descriptor 2>/dev/null | xxd | head -10
done
echo
echo "=== 视频 ==="
lsmod | grep -i -E "uvc|videodev" | head -5
ls -l /dev/v4l/by-id/ 2>/dev/null || echo "无 /dev/v4l/by-id"
