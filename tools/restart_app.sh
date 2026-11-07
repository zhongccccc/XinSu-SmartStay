#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -9 -f chromium 2>/dev/null
sleep 3
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 12
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
setsid nohup bash /opt/zhikong/app/scripts/kiosk_session.sh > /tmp/ks9.log 2>&1 < /dev/null &
sleep 25
echo "=== 状态 ==="
curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d.get('step'))"
echo "=== 实例 ==="
pgrep -c -f 'chromium.*8080'
echo "=== 截图 ==="
grim -o DSI-1 /tmp/after_fix.png && echo ok
