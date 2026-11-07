#!/bin/bash
echo "=== 门锁事件（最近 6 条）==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -6
echo
echo "=== 刷卡开门的审计记录 ==="
echo 123456 | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for kind, payload, ts in c.execute(
        "SELECT kind, payload, ts FROM audit WHERE kind IN ('card_door','lock_checkout') ORDER BY id DESC LIMIT 6"):
    print("  %s | %s" % (kind, payload))
c.close()
PY
