#!/bin/bash
# 驱动一遍入住流程，逐屏截图（VNC :1）
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
B=http://127.0.0.1:8080
D=/opt/zhikong/data/shots
mkdir -p $D
shot() { sleep "$2"; import -window root "$D/$1.png" 2>/dev/null && echo "shot $1"; }

curl -s -X POST $B/api/cancel > /dev/null
shot 00_idle 1.2

curl -s -X POST $B/api/session/start > /dev/null
shot 01_ident 1.5

curl -s -X POST $B/api/idcard/mock > /dev/null
shot 02_face 1.6

curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null
shot 03_room 1.6

curl -s -X POST $B/api/room/8801 > /dev/null
shot 04_pay 1.6

curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay > /dev/null
shot 05_card 1.4

curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"A1B2C3D4"}' $B/api/card > /dev/null
shot 06_issue 0.35

sleep 1.2
curl -s -X POST $B/api/issue > /dev/null
shot 07_done 1.6

curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"帮我送一双拖鞋到房间"}' $B/api/voice > /dev/null
shot 08_voice 1.4

echo "--- all shots ---"
ls -l $D/*.png | tail -10
