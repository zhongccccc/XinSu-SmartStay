#!/bin/bash
echo "=== labwc 配置 ==="
ls -la /home/shiqi/.config/labwc/ 2>/dev/null
echo
echo "=== 是否有会话状态 ==="
find /home/shiqi/.config/labwc /home/shiqi/.local/state -name '*session*' 2>/dev/null | head -5
echo
echo "=== 重启 labwc（会重启整个 Wayland 桌面）==="
pkill -f 'chromium.*8080'
sleep 2
systemctl --user restart labwc 2>/dev/null || pkill -HUP labwc
sleep 6
pgrep -a labwc | head -2
