#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 12
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"BARCODE0001","kind":"qr"}' http://127.0.0.1:8080/api/sim/scan > /dev/null
sleep 1
grim /tmp/toast.png && echo "shot ok"
