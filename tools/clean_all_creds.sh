#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 1. 清空门锁板上的所有凭证 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py "zk revoke" "zk ping"
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 8

echo
echo "=== 2. 清空数据库里的在住订单 ==="
cat > /tmp/cl.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("  订单清理:", cur.rowcount)
c.commit(); c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/cl.py

echo
echo "=== 3. 回待机 ==="
curl -s -X POST $B/api/cancel > /dev/null
sleep 2
curl -s $B/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('   step=%s 在住=%d' % (d.get('step'), len(d.get('inhouse') or [])))
"

echo
echo "=== 4. 门锁板状态 ==="
curl -s $B/api/health | python3 -c "
import sys,json
d=json.load(sys.stdin); lk=d.get('lock') or {}
print('   port=%s online=%s fw=%s' % (lk.get('port'), lk.get('online'), lk.get('firmware')))
"
