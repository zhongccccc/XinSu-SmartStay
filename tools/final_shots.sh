#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080
D=/opt/zhikong/data/shots
mkdir -p $D
shot() { sleep "$2"; grim "$D/f_$1.png" 2>/dev/null && echo "shot $1"; }

curl -s -X POST $B/api/cancel > /dev/null
shot 0_idle 1.5
curl -s -X POST $B/api/session/start > /dev/null
shot 1_ident 2
curl -s -X POST $B/api/idcard/mock > /dev/null
shot 2_face 2
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null
shot 3_room 2
curl -s -X POST $B/api/room/8801 > /dev/null
shot 4_pay 2
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay > /dev/null
shot 5_card 1.8
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"A1B2C3D4"}' $B/api/card > /dev/null
sleep 0.2
curl -s -X POST $B/api/issue > /dev/null
shot 6_done 2
curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"帮我送一双拖鞋到房间"}' $B/api/voice > /dev/null
shot 7_voice 1.8
ls -l $D/f_*.png
