#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.4
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD0001"}' $B/api/card > /dev/null
sleep 3
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=%s code=%s' % (d['step'], d.get('lock_code')))"
echo "=== 设备状态灯 ==="
curl -s $B/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  lock:', d.get('lock'))
print('  camera:', d['camera']['ok'], ' rfid:', d['rfid']['online'], ' idcard:', d['idcard']['online'])
"
grim /tmp/lock_mock.png && echo "shot ok"
curl -s -X POST $B/api/cancel > /dev/null
