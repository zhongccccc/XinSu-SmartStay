#!/bin/bash
PB=123456
echo "=== 壁纸文件 ==="
ls /usr/share/lxqt/wallpapers/*.png 2>/dev/null | head -5
ls /usr/share/backgrounds/*.png /usr/share/backgrounds/*.jpg 2>/dev/null | head -5

echo
echo "=== 桌面目录名 ==="
ls -d /home/shiqi/桌面 /home/shiqi/Desktop 2>/dev/null
xdg-user-dir DESKTOP 2>/dev/null

echo
echo "=== 当前壁纸设置 ==="
cat /home/shiqi/.config/pcmanfm-qt/lxqt/settings.conf 2>/dev/null | grep -E 'Wallpaper|wallpaper' | head -5
