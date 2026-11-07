#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "=== 1. 桌面改成单击打开 ==="
CFG=~/.config/pcmanfm-qt/lxqt/settings.conf
if grep -q '^SingleClick=' "$CFG"; then
  sed -i 's/^SingleClick=.*/SingleClick=true/' "$CFG"
else
  sed -i '/^\[/!b' "$CFG"
  printf 'SingleClick=true\n' >> "$CFG"
fi
grep -E '^SingleClick=' "$CFG"

echo "=== 2. 重启桌面（让设置生效）==="
pkill -f "pcmanfm-qt --desktop" 2>/dev/null
sleep 2
pgrep -af "pcmanfm-qt --desktop" | head -2 | cut -c1-60

echo "=== 3. 回到桌面（关掉可能残留的界面）==="
pkill -f "chromium.*8080" 2>/dev/null
sleep 2
echo "  chromium 剩余: $(pgrep -c -f 'chromium.*8080')"
grim /tmp/desk_single.png && echo "  shot ok"
