#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 重启图形会话 ==="
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 24

echo "=== 桌面组件 ==="
pgrep -af "pcmanfm-qt --desktop" | head -1 | cut -c1-60
echo "=== 界面进程（应为 0）==="
pgrep -c -f "chromium.*8080" | sed 's/^/  chromium: /'
echo "=== SingleClick 设置 ==="
grep -E '^SingleClick=' ~/.config/pcmanfm-qt/lxqt/settings.conf
grim /tmp/desk_clean.png && echo "  shot ok"
