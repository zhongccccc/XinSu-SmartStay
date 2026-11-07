#!/bin/bash
PB=123456
echo "=== 当前会话/显示管理器 ==="
systemctl status display-manager --no-pager 2>/dev/null | head -3
echo "  default session: $(ls /usr/share/wayland-sessions /usr/share/xsessions 2>/dev/null | tr '\n' ' ')"

echo
echo "=== 已安装的桌面相关包 ==="
dpkg -l 2>/dev/null | awk '/^ii/ {print $2}' | grep -iE 'xfce|lxqt|lxde|pcmanfm|gnome-shell|kde-plasma|mate|wayfire|labwc|sway|waybar|swaybg|feh|thunar|pcmanfm|nautilus|openbox|icewm|fluxbox' | head -20

echo
echo "=== 可用会话 ==="
ls /usr/share/xsessions/ 2>/dev/null | sed 's/^/  x11: /'
ls /usr/share/wayland-sessions/ 2>/dev/null | sed 's/^/  wl : /'

echo
echo "=== 网络/apt 是否可用 ==="
timeout 8 curl -s -o /dev/null -w '  apt 源 HTTP: %{http_code}\n' http://archive.ubuntu.com/ubuntu/ 2>/dev/null || echo "  外网不通"

echo
echo "=== 磁盘空间 ==="
df -h / | tail -1
