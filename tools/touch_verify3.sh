#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
PB='123456'
st() { curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])"; }

echo "before: $(st)"
# 保持虚拟触摸设备 10 秒，期间查 libinput 是否识别
ZK_HOLD=10 nohup sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275 </dev/null >/tmp/tap.log 2>&1 &
sleep 4
echo "--- libinput 是否看到虚拟设备 ---"
echo "$PB" | sudo -S -p '' libinput list-devices 2>/dev/null | grep -i -A2 "zhikong" 
sleep 8
echo "after: $(st)"
cat /tmp/tap.log
