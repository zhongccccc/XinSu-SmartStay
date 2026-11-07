#!/bin/bash
echo "=== chromium 实例 ==="
pgrep -a -f 'chromium.*8080' | sed 's/\(--[a-z-]*=\)[^ ]*/\1.../g' | cut -c1-130
echo
echo "=== 输出模式 ==="
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
(wlr-randr 2>/dev/null || true) | head -12
echo
echo "=== 清理后重启 ==="
pkill -f 'chromium.*8080'
sleep 3
rm -rf /tmp/chrome-vnc
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/kiosk.log 2>&1 < /dev/null &
sleep 14
pgrep -c -f 'chromium.*8080' | sed 's/^/  实例数: /'
grim /tmp/clean_view.png && echo "  截图完成"
