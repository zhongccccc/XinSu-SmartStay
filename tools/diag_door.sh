#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

echo "=== 后端订单状态 ==="
curl -s $B/api/state > /tmp/sr.json 2>/dev/null
CODE=$(python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sr.json'))
    print(d.get('lock_code') or '')
except Exception:
    print('')
PY
)
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sr.json'))
    print("  step=%s room=%s code=%s card=%s" % (d.get('step'),
          (d.get('room') or {}).get('no'), d.get('lock_code'), d.get('card_uid')))
except Exception as e:
    print("  ", e)
PY

echo
echo "=== 最近下发日志 ==="
grep -aE 'lock_issue|ISSUE|lock:board' /opt/zhikong/logs/backend.log | tail -5

echo
echo "=== 板上直接校验这个码 ==="
if [ -n "$CODE" ]; then
  echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
  sleep 2
  echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py "zk code $CODE" "zk ping"
  echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
else
  echo "  后端没有开门码（订单可能已结束）"
fi

echo
echo "=== 在住订单 ==="
curl -s $B/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
for o in (d.get('inhouse') or [])[:5]:
    print('   房间', o.get('room'), '卡', o.get('card_uid'), '码', o.get('lock_code'))
print('   共', len(d.get('inhouse') or []), '单')
"
