#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
CFG=~/.config/pcmanfm-qt/lxqt/settings.conf

echo "=== 改配置（趁它还没写回）==="
sed -i 's/^SingleClick=.*/SingleClick=true/' "$CFG"

echo "=== SIGKILL 桌面进程（不给它保存设置的机会）==="
pkill -9 -f "pcmanfm-qt --desktop" 2>/dev/null
sleep 3

echo "=== 重读配置 ==="
grep -E '^SingleClick=' "$CFG"
pgrep -af "pcmanfm-qt --desktop" | head -1 | cut -c1-60

sleep 2
grim /tmp/desk_single2.png && echo "shot ok"
