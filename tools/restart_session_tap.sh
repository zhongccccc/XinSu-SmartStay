#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 重启图形会话，让 kiosk 由会话正常拉起 ==="
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 22

echo "=== 会话与进程 ==="
loginctl list-sessions --no-legend | head -3
pgrep -af "chromium.*8080" | head -1 | cut -c1-80

echo "=== 复位到人脸页 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.8
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 1.2
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d['step'])"

echo "=== 点返回键 (645,24) ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 645 24
sleep 1.8
grep -E "\[ui\] (down|click)" /opt/zhikong/logs/backend.out | tail -3
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d['step'],'guest=',d.get('guest'))"
grim /tmp/back_ok.png
