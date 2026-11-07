#!/bin/bash
PB=123456
echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
sleep 14
echo "=== 后端识别结果 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h_now.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/h_now.json'))
except Exception as e:
    print("  读取失败:", e); raise SystemExit
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  门锁板 : online=%s port=%s fw=%s" % (lk.get('online'), lk.get('port'), lk.get('firmware')))
print("  家居板 : online=%s port=%s fw=%s err=%s" % (hm.get('online'), hm.get('port'), hm.get('firmware'), hm.get('error')))
print("  摄像头 :", (d.get('camera') or {}).get('ok'))
PY
echo
echo "=== 后端日志里的端口探测 ==="
grep -aE '\[lock|\[home|ttyUSB|串口' /opt/zhikong/logs/backend.log | tail -10
echo
echo "=== /api/home ==="
curl -s http://127.0.0.1:8080/api/home | head -c 260
echo
