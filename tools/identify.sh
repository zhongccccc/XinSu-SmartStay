#!/bin/bash
PB=123456
echo "=== USB 详情 ==="
for d in /sys/bus/usb/devices/*; do
  vid=$(cat $d/idVendor 2>/dev/null); [ -z "$vid" ] && continue
  pid=$(cat $d/idProduct 2>/dev/null)
  prod=$(cat $d/product 2>/dev/null)
  man=$(cat $d/manufacturer 2>/dev/null)
  cls=$(cat $d/bDeviceClass 2>/dev/null)
  echo "[$vid:$pid] class=$cls  $man / $prod"
  for i in $d/*:*; do
    [ -f "$i/bInterfaceClass" ] || continue
    echo "    iface $(basename $i): class=$(cat $i/bInterfaceClass) sub=$(cat $i/bInterfaceSubClass) proto=$(cat $i/bInterfaceProtocol) driver=$(basename $(readlink -f $i/driver 2>/dev/null) 2>/dev/null)"
  done
done

echo
echo "=== hidraw ==="
ls -l /dev/hidraw* 2>/dev/null
for h in /dev/hidraw*; do
  [ -e "$h" ] || continue
  n=$(cat /sys/class/hidraw/${h##*/}/device/uevent 2>/dev/null | grep HID_NAME | cut -d= -f2)
  echo "$h -> $n"
done

echo
echo "=== dmesg 最近 ==="
echo "$PB" | sudo -S -p '' dmesg 2>/dev/null | tail -25

echo
echo "=== ttyUSB0 试探（3 秒读原始字节）==="
echo "$PB" | sudo -S -p '' stty -F /dev/ttyUSB0 115200 raw -echo 2>&1
echo "$PB" | sudo -S -p '' timeout 3 cat /dev/ttyUSB0 2>/dev/null | xxd | head -5
echo "(空=设备不主动上报，属正常)"
