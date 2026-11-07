#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

pkill -f '[c]hromium.*8080'; sleep 1
setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/al5.log 2>&1 < /dev/null &
sleep 16

# 待机页截图
grim /tmp/idle_co.png && echo idle_shot

# 点「退房 / 作废开门凭证」
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 200 300 > /dev/null 2>&1
sleep 1.5
grim /tmp/co_sheet.png && echo sheet_shot
