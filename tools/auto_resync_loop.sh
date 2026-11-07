#!/bin/bash
# 轮询重下发：板子一上线就把在住订单的凭证写进去
B=http://127.0.0.1:8080
for i in $(seq 1 40); do
  OUT=$(curl -s -X POST $B/api/lock/resync 2>/dev/null)
  ISSUED=$(printf '%s' "$OUT" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read() or '{}')
    print(d.get('issued', 0))
except Exception:
    print(-1)
" 2>/dev/null)
  ST=$(curl -s $B/api/health 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    lk = d.get('lock') or {}
    print('online' if lk.get('online') else 'offline')
except Exception:
    print('?')
" 2>/dev/null)
  echo "[$(date '+%H:%M:%S')] 第 $i 次: 板子=$ST 已下发=$ISSUED"
  if [ "$ISSUED" != "0" ] && [ "$ISSUED" != "-1" ] && [ -n "$ISSUED" ]; then
    echo "成功！凭证已写入板子"
    break
  fi
  sleep 8
done
echo "=== 结束 ==="
