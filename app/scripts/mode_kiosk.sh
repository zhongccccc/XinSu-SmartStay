#!/bin/bash
# 切回「开机自动全屏一体机」模式
PB=123456
echo "$PB" | sudo -S -p '' touch /opt/zhikong/etc/kiosk_autostart.enabled
echo "$PB" | sudo -S -p '' chown shiqi:shiqi /opt/zhikong/etc/kiosk_autostart.enabled
if [ ! -f /etc/sddm.conf.d/zz-zhikong-kiosk.conf ]; then
  printf '[Autologin]\nUser=shiqi\nSession=labwc\nRelogin=true\n' > /tmp/zs.conf
  echo "$PB" | sudo -S -p '' cp /tmp/zs.conf /etc/sddm.conf.d/zz-zhikong-kiosk.conf
  rm -f /tmp/zs.conf
fi
echo "$PB" | sudo -S -p '' systemctl restart sddm
echo "已切回 kiosk 模式：开机自动全屏进入一体机"
