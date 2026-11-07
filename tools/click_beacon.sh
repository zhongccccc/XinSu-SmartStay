#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
st() { curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])"; }
clicks() { grep -c "\[ui\] click" /opt/zhikong/logs/backend.out 2>/dev/null || echo 0; }

echo "== reload both kiosks =="
pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/start_kiosk.sh :1 > /opt/zhikong/logs/kiosk.out 2>&1 &
sleep 3
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 10

echo "clicks before: $(clicks)  step: $(st)"
echo "== seat0 tap via uinput =="
echo 123456 | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275
sleep 2
echo "clicks after seat0 tap: $(clicks)  step: $(st)"
grim /tmp/s0.png
echo "== x11 click =="
xdotool mousemove 465 619 click 1
sleep 2
echo "clicks after x11 click: $(clicks)  step: $(st)"
import -window root /tmp/x11.png 2>/dev/null
tail -6 /opt/zhikong/logs/backend.out
