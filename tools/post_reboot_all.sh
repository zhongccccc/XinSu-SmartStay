#!/bin/bash
sleep 10
echo "=== 服务 ==="
for s in zhikong-backend idreader; do printf "%-20s %s\n" $s "$(systemctl is-active $s)"; done
echo "=== 端口 ==="
ss -ltnp 2>/dev/null | grep -E "8080|7846" || echo "无"
echo "=== 设备健康 ==="
curl -s -m 10 http://127.0.0.1:8080/api/health > /tmp/hb2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hb2.json'))
print("camera:", {k: d['camera'][k] for k in ('ok', 'node', 'fps')})
print("idcard:", d.get('idcard'))
print("rfid  :", {k: d['rfid'].get(k) for k in ('online', 'port')})
PY
echo "=== 读卡器 ==="
for i in 1 2 3; do
  r=$(curl -s -m 15 'http://127.0.0.1:7846/api/readCard?utf8=1')
  echo "$r" | head -4 | tr -d '\n'
  echo
  echo "$r" | grep -q '"resultFlag" : "0"' && { echo "读到卡!"; break; }
  sleep 3
done
echo "=== kiosk ==="
pgrep -c -f "[c]hromium.*8080"
