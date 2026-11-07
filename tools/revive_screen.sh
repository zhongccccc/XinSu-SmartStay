#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

echo "=== 负载 ==="
uptime
echo "=== 摄像头进程 ==="
pgrep -a 'gst-launch' 2>/dev/null | head -3 || echo "  无"
echo "=== 起 kiosk ==="
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 14
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"
curl -s -o /dev/null -w '  backend HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

echo "=== 摄像头错误是否还在刷 ==="
echo "$PB" | sudo -S -p '' journalctl -b -n 5 --no-pager 2>/dev/null | tail -5

echo "=== 截图 ==="
grim -o DSI-1 /tmp/scr.png && echo "  ok"
