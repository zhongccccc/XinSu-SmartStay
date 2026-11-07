#!/bin/bash
# 在 VNC 的 X 会话 (:1) 里打开一体机界面（窗口 800x480）
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority

PROFILE=/tmp/chrome-vnc
mkdir -p "$PROFILE"

# 先清掉这个会话里旧的实例
pkill -f "user-data-dir=$PROFILE" 2>/dev/null
sleep 1

nohup chromium-browser \
  --ozone-platform=x11 --disable-gpu --disable-gpu-compositing \
  --disable-software-rasterizer --disable-features=Vulkan,VulkanFromANGLE \
  --user-data-dir=$PROFILE --no-first-run --no-default-browser-check \
  --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
  --password-store=basic --window-size=800,480 --window-position=0,0 \
  --app=http://127.0.0.1:8080/ > /tmp/vnc-chrome.log 2>&1 &

sleep 6
echo "=== VNC 会话里的 chromium ==="
pgrep -a -f "user-data-dir=$PROFILE" | head -2 || echo "  未启动"

echo
echo "=== 截个图确认 ==="
if command -v import > /dev/null; then
  import -window root /tmp/vnc_screen.png 2>/dev/null && echo "  已截图 /tmp/vnc_screen.png"
fi
