#!/bin/bash
# 芯宿·智控 —— 桌面应用启动器
# 用法：
#   app_launch.sh              全屏 kiosk（默认，适合 800x480 触摸屏）
#   ZHIKONG_MODE=window app_launch.sh    窗口模式（适合接 HDMI 大屏/调试）
export ZHIKONG_HOME=/opt/zhikong
MODE="${ZHIKONG_MODE:-kiosk}"

# 1) 确保后端在跑（服务已设开机自启，这里是兜底，不弹密码框）
if ! curl -s -m 1 http://127.0.0.1:8080/api/health > /dev/null 2>&1; then
  sudo -n systemctl start zhikong-backend 2>/dev/null || true
  for i in $(seq 1 40); do
    curl -s -m 1 http://127.0.0.1:8080/api/health > /dev/null 2>&1 && break
    sleep 0.5
  done
fi

# 2) 关掉已有实例（避免开第二个窗口/抢占摄像头）
pkill -f "chromium.*127.0.0.1:8080" 2>/dev/null
sleep 0.8

# 3) 选显示后端
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
  OZONE=wayland
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
else
  OZONE=x11
fi

PROFILE=/opt/zhikong/data/chromium-kiosk
mkdir -p "$PROFILE"

COMMON="--ozone-platform=$OZONE --disable-gpu --disable-gpu-compositing \
--disable-software-rasterizer --disable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan \
--user-data-dir=$PROFILE --no-first-run --no-default-browser-check --noerrdialogs \
--disable-infobars --disable-session-crashed-bubble --password-store=basic \
--check-for-update-interval=31536000 --overscroll-history-navigation=0"

if [ "$MODE" = "window" ]; then
  exec chromium-browser $COMMON --window-size=800,480 --window-position=0,0 \
       --app=http://127.0.0.1:8080/
else
  exec chromium-browser $COMMON --kiosk --start-maximized \
       --app=http://127.0.0.1:8080/
fi
