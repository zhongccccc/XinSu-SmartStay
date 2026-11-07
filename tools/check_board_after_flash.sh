#!/bin/bash
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 后端门锁状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
print("  lock:", d.get('lock'))
print("  camera:", d['camera']['ok'], "rfid:", d['rfid']['online'], "idcard:", d['idcard']['online'])
PY
echo
echo "=== 后端日志里的门锁行 ==="
grep -E "lock" /opt/zhikong/logs/backend.out | tail -5
