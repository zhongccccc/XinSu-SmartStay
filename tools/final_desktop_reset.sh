#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 26
echo "=== 会话 ==="
loginctl list-sessions --no-legend | awk '{print "  seat="$3" state="$5}' | head -3
echo "=== SingleClick（应是 true，且没被写回）==="
grep -E '^SingleClick=' ~/.config/pcmanfm-qt/lxqt/settings.conf
echo "=== chromium ==="
pgrep -c -f "chromium.*8080" | sed 's/^/  /'
grim /tmp/desk_final.png && echo "shot ok"
