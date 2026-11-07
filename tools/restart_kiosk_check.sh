#!/bin/bash
PB=123456
echo "=== 开机自启开关 ==="
ls -l /opt/zhikong/etc/kiosk_autostart.enabled 2>/dev/null || echo "  自启开关文件不存在"
grep -c 'zhikong' /home/shiqi/.config/labwc/autostart 2>/dev/null | sed 's/^/  labwc autostart 行数: /'

echo
echo "=== 启动双屏 ==="
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 15
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"

echo
echo "=== 截图确认 ==="
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/after_recover.png && echo "  ok"
