#!/bin/bash
PB=123456

echo "=== 修按钮排版 ==="
python3 - <<'PY'
import re
p = '/opt/zhikong/app/web/style.css'
s = open(p, encoding='utf-8').read()
new = (".skip-card{display:block;margin:16px auto 0;font-size:13px;"
       "padding:10px 20px;border-radius:10px}")
s2, n = re.subn(r"\.skip-card\{[^}]*\}", new, s)
open(p, 'w', encoding='utf-8').write(s2)
print("  skip-card 样式已更新:", n)
PY

echo "=== 清空测试订单 ==="
cat > /tmp/clean_orders.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("  清理:", cur.rowcount)
c.commit()
c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/clean_orders.py

echo "=== 重启服务 ==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 12
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 2
curl -s http://127.0.0.1:8080/api/state > /tmp/sz.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/sz.json'))
print("  step =", d.get("step"), "| 在住订单 =", len(d.get("inhouse") or []))
PY
