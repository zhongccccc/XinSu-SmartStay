#!/bin/bash
PB=123456
echo "=== 后端门锁状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hl.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hl.json'))
except Exception as e:
    print("  health 失败:", e); raise SystemExit
lk = d.get('lock') or {}
print("  port=%s online=%s fw=%s" % (lk.get('port'), lk.get('online'), lk.get('firmware')))
PY

echo
echo "=== 最近的凭证下发日志 ==="
grep -aE 'lock_issue|ISSUE|lock:board|凭证' /opt/zhikong/logs/backend.log | tail -8

echo
echo "=== 审计：最近的下发记录 ==="
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for k, p in c.execute("SELECT kind,payload FROM audit WHERE kind LIKE 'lock%' ORDER BY id DESC LIMIT 5"):
    print("  ", k, str(p)[:120])
c.close()
PY

echo
echo "=== 当前状态 ==="
curl -s http://127.0.0.1:8080/api/state > /tmp/sl.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sl.json'))
    print("  step=%s code=%s room=%s" % (d.get('step'), d.get('lock_code'), (d.get('room') or {}).get('no')))
except Exception as e:
    print("  ", e)
PY
