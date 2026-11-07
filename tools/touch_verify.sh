#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
PB='123456'

echo "--- before ---"
curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print('step=',json.load(sys.stdin)['step'])"
grim /tmp/t_before.png

echo "--- inject tap at CTA button (180,275) ---"
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275
sleep 2.5

echo "--- after ---"
curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print('step=',json.load(sys.stdin)['step'])"
grim /tmp/t_after.png
ls -l /tmp/t_before.png /tmp/t_after.png
