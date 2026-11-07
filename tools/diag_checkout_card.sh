#!/bin/bash
echo "=== 读卡器 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hz9.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hz9.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
rf = d.get('rfid') or {}
lk = d.get('lock') or {}
print("  rfid :", rf.get('port'), "online=", rf.get('online'),
      "reads=", rf.get('reads'), "last=", rf.get('last_uid'))
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
PY

echo
echo "=== 最近刷卡日志 ==="
grep -a '\[rfid\] card uid' /opt/zhikong/logs/backend.log | tail -4
echo "  现在: $(date '+%H:%M:%S')"

echo
echo "=== 在住订单的卡号 ==="
curl -s http://127.0.0.1:8080/api/state > /tmp/sz9.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sz9.json'))
except Exception as e:
    print("  state:", e); raise SystemExit
ins = d.get('inhouse') or []
print("  在住订单:", len(ins))
for o in ins[:8]:
    print("    房间 %-6s 卡=%-12s 码=%s" % (o.get('room'), o.get('card_uid'), o.get('lock_code')))
PY

echo
echo "=== 退房拒因（最近） ==="
grep -a 'checkout_denied\|lock_checkout' /opt/zhikong/logs/backend.log | tail -3
