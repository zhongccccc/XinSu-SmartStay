#!/bin/bash
echo "=== lsusb ==="
lsusb
echo
echo "=== serial ==="
ls -l /dev/serial/by-id/ 2>/dev/null
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
echo
echo "=== input ==="
ls /dev/input/by-id/ 2>/dev/null
for e in /dev/input/event*; do
  n=$(cat /sys/class/input/${e##*/}/device/name 2>/dev/null)
  k=$(cat /sys/class/input/${e##*/}/device/capabilities/key 2>/dev/null | head -c 20)
  a=$(cat /sys/class/input/${e##*/}/device/capabilities/abs 2>/dev/null | head -c 20)
  echo "$e | $n | key=$k | abs=$a"
done
echo
echo "=== video ==="
for v in /dev/video*; do
  i=${v##*video}
  echo "$v | $(cat /sys/class/video4linux/video$i/name 2>/dev/null)"
done | grep -v -E "aout|ain|vivi|mvx|dec"
echo
echo "=== backend/kiosk ==="
systemctl is-active zhikong-backend
pgrep -c -f "[c]hromium.*8080"
curl -s -m 5 http://127.0.0.1:8080/api/devices > /tmp/dev.json
python3 -c "
import json
d=json.load(open('/tmp/dev.json'))
for i in d['items']: print('%-8s %-6s %s' % (i['key'], i['present'], i['detail']))
"
