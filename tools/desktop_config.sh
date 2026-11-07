#!/bin/bash
PB=123456
echo "=== sddm 默认会话配置 ==="
cat /etc/sddm.conf 2>/dev/null | head -20
ls /etc/sddm.conf.d/ 2>/dev/null && cat /etc/sddm.conf.d/*.conf 2>/dev/null | head -20
echo "  ~/.dmrc: $(cat /home/shiqi/.dmrc 2>/dev/null)"

echo
echo "=== lxqt-wayland 会话启动内容 ==="
cat /usr/share/wayland-sessions/lxqt-wayland.desktop 2>/dev/null

echo
echo "=== labwc autostart（当前 kiosk 自启）==="
cat /home/shiqi/.config/labwc/autostart 2>/dev/null

echo
echo "=== 是否有 LXQt 配置 ==="
ls /home/shiqi/.config/lxqt/ 2>/dev/null
