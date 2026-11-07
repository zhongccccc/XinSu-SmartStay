#!/bin/bash
PB=123456
U=/home/shiqi
echo "=== 桌面图标确认 ==="
ls -l "$U/Desktop/" 2>/dev/null | grep -i zhikong || ls "$U/Desktop/" | cat

echo
echo "=== 重启图形会话（重新登录，让面板/桌面生效）==="
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 25

echo "=== 会话进程 ==="
pgrep -a lxqt-panel | head -2
pgrep -a pcmanfm-qt | head -2
pgrep -a labwc | head -2

echo
echo "=== 截图 ==="
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/desk.png && echo "  ok"
