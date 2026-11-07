#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
PB='123456'
st() { curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])"; }

echo "before: $(st)"
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275
sleep 1.2
echo "after tap1: $(st)"
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275
sleep 2
echo "after tap2: $(st)"
grim /tmp/t_after2.png
echo "--- input devices seen by libinput ---"
echo "$PB" | sudo -S -p '' libinput list-devices 2>/dev/null | grep -E "^Device|Capabilities" | head -20
