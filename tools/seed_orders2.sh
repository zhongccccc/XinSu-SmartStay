#!/bin/bash
PB=123456
cat > /tmp/seed.py <<'PY'
import sqlite3, time
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
now = time.time()
rows = [
    ("张伟",   "4403**********1234", "8801", 468, "-",        "135790"),
    ("李梦琪", "4403**********5678", "8805", 508, "46055DF4", "246810"),
    ("陈思远", "4403**********9012", "9902", 728, "-",        "975310"),
]
for g, idno, room, price, card, code in rows:
    cur.execute(
        "INSERT INTO orders (guest,idno,room,price,card_uid,lock_code,checkin_at,status,payload) "
        "VALUES (?,?,?,?,?,?,?,'inhouse','{}')", (g, idno, room, price, card, code, now))
c.commit()
cur.execute("SELECT COUNT(*) FROM orders WHERE status='inhouse'")
print("测试订单已插入，当前在住:", cur.fetchone()[0])
c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/seed.py
curl -s http://127.0.0.1:8080/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('API 在住:', len(d.get('inhouse') or []))
for o in (d.get('inhouse') or [])[:5]:
    print('   ', o.get('room'), o.get('guest'), o.get('lock_code'))
"
