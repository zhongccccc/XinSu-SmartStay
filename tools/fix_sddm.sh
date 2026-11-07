#!/bin/bash
PB='123456'
echo "$PB" | sudo -S -p '' mv -f /etc/sddm.conf.d/99-zhikong-kiosk.conf /etc/sddm.conf.d/zz-zhikong-kiosk.conf 2>/dev/null
ls -l /etc/sddm.conf.d/
echo "--- content ---"
cat /etc/sddm.conf.d/zz-zhikong-kiosk.conf
echo "--- restart ---"
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 12
loginctl list-sessions
echo "--- seat ---"
loginctl show-seat seat0 -p ActiveSession
echo "--- wayland ---"
ls /run/user/1000/ 2>/dev/null | grep -i wayland
echo "--- journal ---"
journalctl -u sddm -n 15 --no-pager | tail -10
