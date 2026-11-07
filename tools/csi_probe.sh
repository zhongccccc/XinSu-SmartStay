#!/bin/bash
PB=123456
S="echo $PB | sudo -S -p ''"
echo "=== sensor 驱动 ==="
$S dmesg 2>/dev/null | grep -iE "csi|ov[0-9]{4}|imx[0-9]{3}|gc[0-9]{4}|sc[0-9]{4}|ccic|isp" | tail -20
echo
echo "=== i2c 上的 camera sensor ==="
for i in 0 1 2 3 4 5 8 9; do
  echo "--- i2c-$i"
  $S i2cdetect -y -r $i 2>/dev/null | tail -n +4 | head -6
done
echo
echo "=== media 拓扑（sensor 与 video 节点）==="
media-ctl -p -d /dev/media0 2>/dev/null | grep -E "entity|device node|pad0|->" | head -60
echo
echo "=== 有没有现成的 camera 工具/示例 ==="
ls /usr/bin | grep -iE "cam|gst|v4l" | head -20
ls /usr/share | grep -iE "camera|bianbu" | head
