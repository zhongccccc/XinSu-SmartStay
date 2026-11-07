#!/bin/bash
PB=123456
echo "=== 重启后端（固定端口）==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h9.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/h9.json'))
except Exception:
    print("  后端未就绪"); raise SystemExit
lk = d.get('lock') or {}
hm = d.get('home') or {}
rf = d.get('rfid') or {}
print("  门锁板 : online=%-5s port=%-14s fw=%s" % (lk.get('online'), lk.get('port'), lk.get('firmware')))
print("  家居板 : online=%-5s port=%-14s fw=%s" % (hm.get('online'), hm.get('port'), hm.get('firmware')))
print("  读卡器 : online=%-5s reads=%s" % (rf.get('online'), rf.get('reads')))
PY

echo
echo "=== 家居板数据 ==="
curl -s http://127.0.0.1:8080/api/home | head -c 280
echo
