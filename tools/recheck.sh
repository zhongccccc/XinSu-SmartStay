#!/bin/bash
echo "=== CH340 设备 ==="
lsusb | grep '1a86:7523' | nl
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo "=== 后端识别 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h4.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/h4.json'))
except Exception as e:
    print("  health 读取失败:", e); raise SystemExit
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  门锁板: online=%s port=%s fw=%s" % (lk.get('online'), lk.get('port'), lk.get('firmware')))
print("  家居板: online=%s port=%s fw=%s err=%s" % (hm.get('online'), hm.get('port'), hm.get('firmware'), hm.get('error')))
print("  摄像头:", (d.get('camera') or {}).get('ok'))
PY
echo "=== 最近探测日志 ==="
grep -aE '\[lock|\[home\]|ttyUSB' /opt/zhikong/logs/backend.log | tail -6
