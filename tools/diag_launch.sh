#!/bin/bash
echo "=== 1. 配置目录里的锁文件 ==="
ls -la /opt/zhikong/data/chromium-kiosk/ 2>/dev/null | grep -i singleton || echo "  无 Singleton 锁"

echo
echo "=== 2. 有没有残留 chromium ==="
pgrep -af "chromium.*8080" | cut -c1-90

echo
echo "=== 3. 直接跑启动器，看报错 ==="
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
cd /opt/zhikong/app/scripts
timeout 25 bash -x ./app_launch.sh > /tmp/launch.log 2>&1 &
LPID=$!
sleep 12
echo "--- 是否起来 ---"
pgrep -af "chromium.*8080" | head -2 | cut -c1-80
echo "--- 日志尾部 ---"
tail -25 /tmp/launch.log
wait $LPID 2>/dev/null
