#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import sqlite3, time, glob
paths = glob.glob('/opt/zhikong/data/*.db') + glob.glob('/opt/zhikong/*.db') + glob.glob('/opt/zhikong/app/data/*.db')
print("数据库:", paths)
for p in paths:
    try:
        c = sqlite3.connect(p)
        n = c.execute("SELECT COUNT(*) FROM orders WHERE status='inhouse'").fetchone()[0]
        c.execute("UPDATE orders SET status='checkedout', checkout_at=? WHERE status='inhouse'", (time.time(),))
        c.commit()
        print("  %s: 清理 %d 条在住订单" % (p, n))
        c.close()
    except Exception as e:
        print("  %s: %s" % (p, e))
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 6
curl -s http://127.0.0.1:8080/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('待机在住订单:', len(d.get('inhouse') or []))"
