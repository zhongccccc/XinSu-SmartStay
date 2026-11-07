#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

st() { curl -s $B/api/state > /tmp/s5.json; python3 - <<'PY'
import json
d = json.load(open('/tmp/s5.json'))
print("   step=%-6s code=%s msg=%s" % (d.get('step'), d.get('lock_code') or '-', (d.get('msg') or '')[:34]))
PY
}

curl -s -X POST $B/api/cancel > /dev/null; sleep 1.2
echo "=== 开始 ==="; curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5; st
echo "=== 刷证 ==="; curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6; st
echo "=== 人脸(自动)==="; curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5; st
echo "=== 选房 ==="; curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.4; st
echo "=== 支付 ==="; curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.6; st
echo "=== 等下发 ==="; sleep 6; st
grim -o DSI-1 /tmp/flow_no_card.png && echo "  截图完成"
echo "=== 家居板（应保持不动）==="
curl -s $B/api/home | python3 -c "
import sys,json
d=json.load(sys.stdin); x=d.get('data') or {}
print('  online=%s fw=%s 灯=%s 风扇=%s 人体=%s' % (d.get('online'), d.get('firmware'), x.get('light'), x.get('fan'), x.get('pir')))
"
