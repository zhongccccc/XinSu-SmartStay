#!/bin/bash
PB=123456
echo "=== 当前串口 ==="
ls /dev/ttyUSB* 2>/dev/null

echo
echo "=== 哪个口是门锁板 ==="
echo "$PB" | sudo -S -p '' python3 /tmp/flp.py

echo
echo "=== 自动写入配置 ==="
PORT=$(echo "$PB" | sudo -S -p '' python3 /tmp/flp.py 2>/dev/null | grep 'ping=True' | head -1 | awk '{print $1}')
if [ -n "$PORT" ]; then
  echo "  找到: $PORT"
  python3 - "$PORT" <<'PY'
import json, sys
port = sys.argv[1]
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock'].update({"transport": "board", "port": port, "baud": 115200})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("  配置已更新:", d['devices']['lock'])
PY
  echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
  sleep 7
  curl -s http://127.0.0.1:8080/api/health > /tmp/h3.json
  python3 - <<'PY'
import json
d = json.load(open('/tmp/h3.json'))
print("  lock:", d.get('lock'))
PY
else
  echo "  !! 没有端口响应门锁协议，板子可能没上电或固件没跑"
fi
