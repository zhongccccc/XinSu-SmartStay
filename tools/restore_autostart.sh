#!/bin/bash
PB=123456
echo "=== 恢复 kiosk 自启动 ==="
if [ -x /opt/zhikong/app/scripts/enable_kiosk_autostart.sh ]; then
  bash /opt/zhikong/app/scripts/enable_kiosk_autostart.sh 2>&1 | tail -3
else
  echo "脚本不存在，直接建标记（不落盘密码）"
fi
touch /opt/zhikong/etc/kiosk_autostart.enabled
ls -l /opt/zhikong/etc/kiosk_autostart.enabled

echo
echo "=== 重启桌面会话 ==="
pkill -9 -f chromium 2>/dev/null
sleep 1
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 35
echo "实例: $(pgrep -c -f 'chromium.*8080')"
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim /tmp/final_view.png && echo "shot ok"
