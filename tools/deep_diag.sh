#!/bin/bash
echo "=== 1. 门锁连接方式（关键：mock 就是没连上）==="
curl -s http://127.0.0.1:8080/api/health > /tmp/d1.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/d1.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}
print("  transport=%s  port=%s  online=%s  mock=%s" % (
    lk.get('transport'), lk.get('port'), lk.get('online'), lk.get('mock')))
print("  firmware=%s" % lk.get('firmware'))
PY

echo
echo "=== 2. 最近的下发记录（看是发给板子还是发给 mock）==="
grep -aE 'lock_issue|ISSUE|lock:board|mock' /opt/zhikong/logs/backend.log | tail -8

echo
echo "=== 3. 板子有没有上报按键/校验事件 ==="
grep -aE 'ZK\|EVT\|(KEY|CODE|DOOR|CARD)' /opt/zhikong/logs/backend.log | tail -8

echo
echo "=== 4. 当前订单 ==="
curl -s http://127.0.0.1:8080/api/state > /tmp/d2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/d2.json'))
except Exception as e:
    print("  state:", e); raise SystemExit
print("  step=%s" % d.get('step'))
for o in (d.get('inhouse') or [])[:6]:
    print("    房间 %-6s 卡=%-12s 码=%s" % (o.get('room'), o.get('card_uid'), o.get('lock_code')))
PY
