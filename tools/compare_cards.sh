#!/bin/bash
echo "=== 外接读卡器（一体机）最近的刷卡 ==="
grep -a '\[rfid\] card uid=' /opt/zhikong/logs/backend.out | tail -5
echo
echo "=== 门锁板（板载 NFC）最近读到卡 ==="
grep -a 'CARD' /opt/zhikong/logs/backend.out | tail -8
echo
echo "=== 门锁健康 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hk.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hk.json'))
print("  lock:", d.get('lock'))
print("  rfid:", d.get('rfid'))
PY
