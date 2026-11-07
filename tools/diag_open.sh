#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 设备 ==="
curl -s $B/api/health > /tmp/hw.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hw.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), lk.get('firmware'))
PY

echo
echo "=== 在住订单 / 当前码 ==="
curl -s $B/api/state > /tmp/sw.json 2>/dev/null
CODE=$(python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sw.json'))
    ins = d.get('inhouse') or []
    print((ins[-1] if ins else {}).get('lock_code') or d.get('lock_code') or '')
except Exception:
    print('')
PY
)
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sw.json'))
    print("  step=%s" % d.get('step'))
    for o in (d.get('inhouse') or []):
        print("   房间 %s  卡=%s  码=%s" % (o.get('room'), o.get('card_uid'), o.get('lock_code')))
except Exception as e:
    print("  ", e)
PY

echo
echo "=== 板上校验这些码 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
if [ -n "$CODE" ]; then
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py "zk ping" "zk code $CODE" "zk nfc" 2>&1 | head -14
else
  echo "  没拿到开门码"
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py "zk ping" 2>&1 | head -6
fi
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
