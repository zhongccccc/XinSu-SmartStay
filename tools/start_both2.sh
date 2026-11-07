#!/bin/bash
# 顺序很重要：先物理屏（它的 pkill 会清场），再 VNC 窗口
export XAUTHORITY=/home/shiqi/.Xauthority

# 1) 物理屏（Wayland）kiosk
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/kiosk.log 2>&1 < /dev/null &
echo "物理屏 kiosk 启动中…"
sleep 10

# 2) VNC 会话窗口版（必须在 kiosk 之后，否则会被 pkill）
export DISPLAY=:1
unset WAYLAND_DISPLAY
PROFILE=/tmp/chrome-vnc
mkdir -p "$PROFILE"
nohup chromium-browser \
  --ozone-platform=x11 --disable-gpu --disable-gpu-compositing \
  --disable-software-rasterizer --disable-features=Vulkan,VulkanFromANGLE \
  --user-data-dir=$PROFILE --no-first-run --no-default-browser-check \
  --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
  --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app=http://127.0.0.1:8080/ > /tmp/vnc-chrome.log 2>&1 &
echo "VNC 窗口已启动"

sleep 7
echo
echo "=== 进程 ==="
pgrep -a -f 'chromium.*8080' | sed 's/--.*//' | head -4
echo "  实例数: $(pgrep -c -f 'chromium.*8080')"
