#!/bin/bash
PB=123456
echo "=== 清理历史测试订单 ==="
echo "$PB" | sudo -S -p '' python3 /tmp/coa.py 2>&1 | tail -2
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 2
curl -s http://127.0.0.1:8080/api/state > /tmp/sy.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/sy.json'))
print("  step =", d.get("step"), "| 在住订单 =", len(d.get("inhouse") or []))
PY

echo "=== 走到房卡步骤截图 ==="
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.6
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.5
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 1
grim -o DSI-1 /tmp/card_step.png && echo "截图完成"
