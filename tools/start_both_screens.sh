#!/bin/bash
# 同时启动：物理屏（Wayland）+ VNC（X11 :1）
export XAUTHORITY=/home/shiqi/.Xauthority

# 1) VNC 会话里的窗口版
export DISPLAY=:1
PROFILE=/tmp/chrome-vnc
mkdir -p "$PROFILE"
pkill -f "user-data-dir=$PROFILE" 2>/dev/null
sleep 1
nohup chromium-browser \
  --ozone-platform=x11 --disable-gpu --disable-gpu-compositing \
  --disable-software-rasterizer --disable-features=Vulkan,VulkanFromANGLE \
  --user-data-dir=$PROFILE --no-first-run --no-default-browser-check \
  --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
  --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app=http://127.0.0.1:8080/ > /tmp/vnc-chrome.log 2>&1 &
echo "VNC 窗口已启动"

# 2) 物理屏（Wayland）kiosk
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
unset DISPLAY
if ! pgrep -f 'chromium.*kiosk' > /dev/null; then
  setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/kiosk.log 2>&1 < /dev/null &
  echo "物理屏 kiosk 已启动"
else
  echo "物理屏 kiosk 已在运行"
fi

sleep 8
echo
echo "=== 进程 ==="
pgrep -c -f 'chromium.*8080' | sed 's/^/  总实例数: /'
