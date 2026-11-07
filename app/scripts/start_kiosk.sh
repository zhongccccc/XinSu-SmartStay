#!/bin/bash
# 在已登录的图形会话上启动 kiosk 浏览器
# 用法: start_kiosk.sh [DISPLAY]   默认 :0（物理屏），预览用 :1（VNC）
export ZHIKONG_HOME=/opt/zhikong
DISP="${1:-:0}"
export DISPLAY="$DISP"
export XAUTHORITY="${XAUTHORITY:-/home/shiqi/.Xauthority}"

# 等后端就绪（最多 30s）
for i in $(seq 1 60); do
  if curl -s -m 1 http://127.0.0.1:8080/api/health > /dev/null 2>&1; then break; fi
  sleep 0.5
done

# 关闭已存在的 kiosk
pkill -f "chromium.*localhost:8080" 2>/dev/null || true
pkill -f "chromium.*127.0.0.1:8080" 2>/dev/null || true
sleep 0.5

PROFILE=/opt/zhikong/data/chromium-kiosk
mkdir -p "$PROFILE"
OZONE="${ZK_OZONE:-x11}"
if [ -n "${WAYLAND_DISPLAY:-}" ]; then OZONE="wayland"; fi
exec chromium-browser \
  --kiosk \
  --ozone-platform="$OZONE" \
  --disable-gpu \
  --disable-gpu-compositing \
  --disable-software-rasterizer \
  --disable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan \
  --in-process-gpu \
  --app=http://127.0.0.1:8080/ \
  --user-data-dir="$PROFILE" \
  --no-first-run --no-default-browser-check --noerrdialogs \
  --disable-infobars --disable-session-crashed-bubble \
  --disable-features=Translate,TranslateUI,PrivacySandboxSettings4 \
  --check-for-update-interval=31536000 \
  --overscroll-history-navigation=0 \
  --touch-events=enabled \
  --window-position=0,0 \
  --window-size=800,480 \
  --password-store=basic
