#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 单击图标 (200,55) ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 200 55 1 0.06
sleep 9
echo "=== 结果 ==="
pgrep -c -f "chromium.*8080" | sed 's/^/  chromium: /'
pgrep -af "chromium.*8080" | head -1 | cut -c1-70
grim /tmp/click1.png
echo "=== 若无进程，补一次双击 ==="
if [ "$(pgrep -c -f 'chromium.*8080')" = "0" ]; then
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 200 55 2 0.06
  sleep 9
  pgrep -c -f "chromium.*8080" | sed 's/^/  chromium: /'
  grim /tmp/click2.png
fi
