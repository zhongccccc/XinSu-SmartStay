#!/bin/bash
echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/h5.json 2>/dev/null
python3 - <<'PY'
import json
d = json.load(open('/tmp/h5.json'))
print("  rfid   :", d.get('rfid'))
print("  idcard :", d.get('idcard'))
print("  lock   :", (d.get('lock') or {}).get('port'), (d.get('lock') or {}).get('online'))
print("  home   :", (d.get('home') or {}).get('port'), (d.get('home') or {}).get('online'))
PY
echo
echo "=== rfid 相关日志 ==="
grep -aEi 'rfid|读卡|房卡' /opt/zhikong/logs/backend.log | tail -10
echo
echo "=== rfid 配置 ==="
python3 - <<'PY'
import json
d = json.load(open('/opt/zhikong/etc/config.json'))
print("  devices:", {k: v for k, v in (d.get('devices') or {}).items() if 'rfid' in k or 'port' in k})
PY
