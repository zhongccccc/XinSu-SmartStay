#!/bin/bash
PB=123456
cat > /tmp/cl2.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("清掉在住订单:", cur.rowcount)
c.commit()
c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/cl2.py

curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 2
curl -s http://127.0.0.1:8080/api/state > /tmp/sx.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/sx.json'))
print("step =", d.get("step"), "| 在住 =", len(d.get("inhouse") or []))
PY
