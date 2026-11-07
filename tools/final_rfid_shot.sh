#!/bin/bash
PB=123456
B=http://127.0.0.1:8080
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 2
echo "=== 设备状态 ==="
curl -s -m 6 $B/api/devices > /tmp/dv.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/dv.json'))
for i in d['items']:
    print("%-8s %-5s %s" % (i['key'], 'ON' if i['present'] else '--', i['detail']))
PY
echo
echo "=== 再走一遍全流程，截图完成页 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.4
curl -s -X POST $B/api/room/8801 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay > /dev/null
for i in $(seq 1 14); do
  sleep 0.5
  s=$(curl -s -m 3 $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])")
  [ "$s" = "issue" ] && break
done
curl -s -X POST $B/api/issue > /dev/null
sleep 1.5
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
grim /tmp/done_rfid.png && echo "shot ok"
curl -s -m 4 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('room=%s card=%s code=%s' % ((d.get('room') or {}).get('no'), d.get('card_uid'), d.get('lock_code')))"
