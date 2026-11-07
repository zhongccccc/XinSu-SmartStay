#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
st() { curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])"; }

pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 12
: > /tmp/ui.log
echo "step: $(st)"
echo 123456 | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 180 275
sleep 2
echo "step after: $(st)"
grep "\[ui\]" /opt/zhikong/logs/backend.out | tail -4
