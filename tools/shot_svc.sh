#!/bin/bash
# 用 VNC 会话打开服务面板截图（?svc=1 调试参数）
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
pkill -f 'user-data-dir=/tmp/chrome-svc' 2>/dev/null
sleep 1
rm -rf /tmp/chrome-svc
nohup chromium-browser --ozone-platform=x11 --disable-gpu \
  --user-data-dir=/tmp/chrome-svc --no-first-run --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app='http://127.0.0.1:8080/?svc=1' > /tmp/csvc.log 2>&1 &
sleep 14
import -window root /tmp/svc_root.png && echo "shot ok"
convert /tmp/svc_root.png -crop 800x480+0+0 +repage /tmp/svc_crop.png && echo "crop ok"
