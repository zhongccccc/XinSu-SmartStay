#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
echo "=== 当前输出 ==="
wlr-randr | head -14
echo
echo "=== 强制 scale=1 ==="
wlr-randr --output DSI-1 --scale 1 2>&1 || echo "  wlr-randr 设置失败"
sleep 2
wlr-randr | grep -E 'Scale|800x480'
echo
echo "=== 重启 kiosk ==="
pkill -9 -f chromium 2>/dev/null
sleep 3
setsid nohup bash /opt/zhikong/app/scripts/kiosk_session.sh > /tmp/ks3.log 2>&1 < /dev/null &
sleep 20
grim /tmp/scaled.png && echo "shot ok"
