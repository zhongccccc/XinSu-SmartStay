#!/bin/bash
PB=123456
U=/home/shiqi

echo "=== 1. 修复 autostart（不再中途 exit，面板和桌面才能起来）==="
cp "$U/.config/labwc/autostart" "$U/.config/labwc/autostart.bak" 2>/dev/null
python3 - <<'PY'
p = '/home/shiqi/.config/labwc/autostart'
s = open(p, encoding='utf-8', errors='ignore').read()
bad = '  { return 0; } 2>/dev/null || exit 0'
if bad in s:
    s = s.replace(bad, '  true')
    open(p, 'w').write(s)
    print("  已移除中途 exit")
else:
    print("  未找到问题代码（可能已修）")
PY

echo
echo "=== 2. 关闭开机自动全屏（改成从桌面图标启动）==="
if [ -f /opt/zhikong/etc/kiosk_autostart.enabled ]; then
  echo "$PB" | sudo -S -p '' mv /opt/zhikong/etc/kiosk_autostart.enabled /opt/zhikong/etc/kiosk_autostart.disabled
  echo "  已改为手动启动"
else
  echo "  已是手动启动"
fi

echo
echo "=== 3. 创建桌面启动图标 ==="
mkdir -p "$U/Desktop"
ICON=$(ls /usr/share/icons/hicolor/128x128/apps/*.png 2>/dev/null | head -1)
[ -z "$ICON" ] && ICON=/usr/share/lxqt/wallpapers/cloud.png

cat > "$U/Desktop/智控自助一体机.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=智控自助一体机
Comment=启动酒店自助入住系统
Exec=/opt/zhikong/tools/kiosk_launch.sh
Icon=$ICON
Terminal=false
Categories=Application;
StartupNotify=false
EOF
chmod +x "$U/Desktop/智控自助一体机.desktop"
# 让 pcmanfm-qt 认为是可信文件，双击直接运行
gio set "$U/Desktop/智控自助一体机.desktop" metadata::trusted true 2>/dev/null
echo "  已创建: $U/Desktop/智控自助一体机.desktop"

echo
echo "=== 4. 启动脚本 ==="
echo "$PB" | sudo -S -p '' tee /opt/zhikong/tools/kiosk_launch.sh > /dev/null <<'EOF'
#!/bin/bash
# 从桌面启动自助一体机界面
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
exec /opt/zhikong/app/scripts/kiosk_session.sh
EOF
echo "$PB" | sudo -S -p '' chmod +x /opt/zhikong/tools/kiosk_launch.sh
echo "  已创建 /opt/zhikong/tools/kiosk_launch.sh"

echo
echo "=== 5. 确认改好 ==="
sed -n '1,6p' "$U/.config/labwc/autostart"
ls -l "$U/Desktop/" 2>/dev/null | tail -3
