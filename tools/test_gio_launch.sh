#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

echo "=== 先清场，回到桌面 ==="
pkill -f "chromium.*8080" 2>/dev/null
sleep 2
pgrep -c -f "chromium.*8080" | sed 's/^/  剩余 chromium: /'

echo
echo "=== gio launch（文件管理器的实际调用方式）==="
rm -f /tmp/gio.log
timeout 20 gio launch "/home/shiqi/Desktop/芯宿智控.desktop" > /tmp/gio.log 2>&1
echo "exit=$?"
cat /tmp/gio.log
sleep 6
echo "--- 起来了吗 ---"
pgrep -af "chromium.*8080" | head -2 | cut -c1-80

echo
echo "=== .desktop 内容 ==="
grep -E '^(Exec|Icon|Type|Terminal)' "/home/shiqi/Desktop/芯宿智控.desktop"
