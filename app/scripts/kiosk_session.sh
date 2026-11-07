#!/bin/bash
# 物理触摸屏（seat0 / labwc Wayland 会话）启动 kiosk
export ZHIKONG_HOME=/opt/zhikong
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/1000}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export ZK_OZONE=wayland

for i in $(seq 1 60); do
  curl -s -m 1 http://127.0.0.1:8080/api/health > /dev/null 2>&1 && break
  sleep 0.5
done
sleep 1

pkill -f "127.0.0.1:8080" 2>/dev/null
sleep 0.5
PROFILE=/opt/zhikong/data/chromium-kiosk
mkdir -p "$PROFILE"

for attempt in 1 2 3; do
  chromium-browser \
    --kiosk \
    --ozone-platform=wayland \
    --disable-gpu --disable-gpu-compositing --disable-software-rasterizer \
    --disable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan \
    --app=http://127.0.0.1:8080/ \
    --user-data-dir="$PROFILE" \
    --no-first-run --no-default-browser-check --noerrdialogs \
    --disable-infobars --disable-session-crashed-bubble \
    --check-for-update-interval=31536000 \
    --overscroll-history-navigation=0 \
    --password-store=basic
  echo "kiosk exited (attempt $attempt), restart in 2s"
  sleep 2
done
