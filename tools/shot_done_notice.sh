#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 启动 kiosk ==="
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 12
echo "  chromium: $(pgrep -c -f 'chromium.*8080')"

echo "=== 等后端 ==="
for i in $(seq 1 40); do
  curl -s -m 1 -o /dev/null $B/api/health 2>/dev/null && break
  sleep 1
done

echo "=== 办一次入住（只为截图完成页）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 6

curl -s $B/api/state | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  step=%s 码=%s' % (d.get('step'), d.get('lock_code')))
"

echo "=== 截图 ==="
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim -o DSI-1 /tmp/done_notice.png && echo "  ok"
