#!/bin/bash
PB=123456
cd /opt/zhikong/app
python3 -m py_compile backend/main.py backend/core/db.py && echo "COMPILE_OK"

echo "=== 清空历史测试订单 ==="
cat > /tmp/cl3.py <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
cur = c.cursor()
cur.execute("UPDATE orders SET status='checked_out' WHERE status='inhouse'")
print("  清理:", cur.rowcount)
c.commit(); c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/cl3.py

echo "=== 重启后端 ==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20

echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hs.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hs.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; c = d.get('camera') or {}
rf = d.get('rfid') or {}
print("  camera:", c.get('ok'))
print("  lock  :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home  :", hm.get('port'), hm.get('online'))
print("  rfid  :", rf.get('port'), rf.get('online'))
PY
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 2
curl -s http://127.0.0.1:8080/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('  最终: step=%s 在住=%d' % (d.get('step'), len(d.get('inhouse') or [])))
"
