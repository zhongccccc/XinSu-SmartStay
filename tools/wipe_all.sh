#!/bin/bash
PB=123456
cat > /tmp/wipe.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("清空在住订单:", cur.rowcount)
c.commit()
cur.execute("SELECT COUNT(*) FROM orders WHERE status='inhouse'")
print("剩余在住:", cur.fetchone()[0])
c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/wipe.py

echo
echo "=== 尝试清空门锁板上的凭证 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py "zk revoke" 2>&1 | head -6
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6

curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 2
curl -s http://127.0.0.1:8080/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('最终: step=%s 在住=%d' % (d.get('step'), len(d.get('inhouse') or [])))
"
