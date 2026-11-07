#!/bin/bash
# 切换到「桌面程序」模式：自动登录桌面，但不自动全屏 kiosk
# 用户双击桌面图标「芯宿智控」启动一体机
PB=123456
echo "$PB" | sudo -S -p '' rm -f /opt/zhikong/etc/kiosk_autostart.enabled
# 确保自动登录仍然开启（这样开机直接进桌面，看不到登录框）
if [ ! -f /etc/sddm.conf.d/zz-zhikong-kiosk.conf ]; then
  printf '[Autologin]\nUser=shiqi\nSession=labwc\nRelogin=true\n' > /tmp/zs.conf
  echo "$PB" | sudo -S -p '' cp /tmp/zs.conf /etc/sddm.conf.d/zz-zhikong-kiosk.conf
  rm -f /tmp/zs.conf
fi
echo "$PB" | sudo -S -p '' systemctl restart sddm
echo "已切到桌面模式：开机会进入桌面，双击「芯宿智控」图标启动"
