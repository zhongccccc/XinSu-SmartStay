#!/bin/bash
# 关闭 kiosk 自启，恢复原桌面登录
set -e
PB='123456'
echo "$PB" | sudo -S -p '' rm -f /opt/zhikong/etc/kiosk_autostart.enabled
echo "$PB" | sudo -S -p '' rm -f /etc/sddm.conf.d/99-zhikong-kiosk.conf
AS=/home/shiqi/.config/labwc/autostart
if [ -f "$AS.bak.zhikong" ]; then
  mv "$AS.bak.zhikong" "$AS"
fi
echo "$PB" | sudo -S -p '' systemctl restart sddm
echo "kiosk autostart disabled"
