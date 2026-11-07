#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 1. 清空数据库（订单 / 工单 / 审计）==="
cat > /tmp/wipe_all.py <<'PY'
import sqlite3, os
p = '/opt/zhikong/data/zhikong.db'
c = sqlite3.connect(p)
cur = c.cursor()
for t in ("orders", "workorders", "audit"):
    try:
        cur.execute("DELETE FROM %s" % t)
        print("  %-10s 删除 %d 行" % (t, cur.rowcount))
    except Exception as e:
        print("  %-10s 跳过: %s" % (t, e))
c.commit()
c.close()
PY
echo "$PB" | sudo -S -p '' python3 /tmp/wipe_all.py

echo
echo "=== 2. 清空人脸照片 ==="
echo "$PB" | sudo -S -p '' bash -c 'rm -f /opt/zhikong/data/photos/*.jpg 2>/dev/null; ls /opt/zhikong/data/photos 2>/dev/null | wc -l' | sed 's/^/  剩余文件: /'

echo
echo "=== 3. 清空门锁板上的所有凭证 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk revoke" "zk ping" 2>&1 | head -8
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 30

echo
echo "=== 4. 最终状态 ==="
curl -s -X POST $B/api/cancel > /dev/null 2>&1
sleep 2
curl -s $B/api/health > /tmp/wipe_h.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/wipe_h.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), "online=", lk.get('online'), "mock=", lk.get('mock'), lk.get('firmware'))
print("  家居板:", hm.get('port'), "online=", hm.get('online'))
print("  读卡器:", rf.get('port'), "online=", rf.get('online'))
PY
curl -s $B/api/state > /tmp/wipe_s.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/wipe_s.json'))
except Exception as e:
    print("  state:", e); raise SystemExit
print("  流程: step=%s  在住订单=%d" % (d.get('step'), len(d.get('inhouse') or [])))
PY
