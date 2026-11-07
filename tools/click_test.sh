#!/bin/bash
# 在 VNC :1 会话上用 xdotool 点击 CTA，验证点击处理器与坐标
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
PB='123456'
command -v xdotool > /dev/null || echo "$PB" | sudo -S -p '' apt-get install -y xdotool > /dev/null 2>&1
st() { curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])"; }

echo "before: $(st)"
WID=$(xdotool search --name "芯宿\|127.0.0.1:8080" 2>/dev/null | head -1)
echo "window: $WID"
xdotool getwindowgeometry $WID 2>/dev/null
# kiosk 窗口在 :1 上是 1920x1080 全屏，800x480 舞台被缩放到居中 2.25 倍
# CTA 在舞台内 (180,275) -> 屏幕 (180*2.25, 275*2.25) = (405, 619)
xdotool mousemove 405 619 click 1
sleep 2.5
echo "after click: $(st)"
grim -o DSI-1 /tmp/x1.png 2>/dev/null || true
