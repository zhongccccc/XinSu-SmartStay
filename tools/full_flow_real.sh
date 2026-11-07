#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('%s guest=%s room=%s card=%s' % (d['step'], d.get('guest'), (d.get('room') or {}).get('no'), d.get('card_uid')))"; }

echo "=== 1. 人脸（抓拍存档）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":true}' $B/api/face > /dev/null
sleep 1; st

echo "=== 2. 选房 8808 ==="
curl -s -X POST $B/api/room/8808 > /dev/null
sleep 1; st

echo "=== 3. 扫码支付 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay > /dev/null
sleep 1; st

echo "=== 4. 等真房卡（RFID）==="
for i in $(seq 1 12); do
  sleep 1
  s=$(curl -s -m 4 $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin)['step'])" 2>/dev/null)
  [ "$s" = "issue" ] && { echo "  -> 房卡已读到"; break; }
done
st

echo "=== 5. 下发门锁 ==="
curl -s -X POST $B/api/issue > /dev/null
sleep 1.5
st
curl -s -m 4 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('开门码:', d.get('lock_code'))" 2>/dev/null
grim /tmp/flow_done.png && echo "shot ok"
echo "=== 审计 ==="
curl -s $B/api/audit > /tmp/aud2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/aud2.json'))
for a in d['items'][:6]:
    print("  %-10s %s" % (a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:90]))
PY
