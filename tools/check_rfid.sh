#!/bin/bash
echo "=== 读卡器配置与状态 ==="
python3 - <<'PY'
import json
d = json.load(open('/opt/zhikong/etc/config.json'))
print("  rfid 配置:", d.get('rfid'))
PY
echo -n "  串口: "; ls -l /dev/ttyUSB0 2>/dev/null | awk '{print $1, $NF}'
echo
echo "=== 后端识别到的读卡器 ==="
grep -a '\[app\] ready' /opt/zhikong/logs/backend.out | tail -1
echo
echo "=== 最近的读卡记录 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hz.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hz.json'))
print("  rfid:", d.get('rfid'))
print("  lock:", d.get('lock'))
PY
