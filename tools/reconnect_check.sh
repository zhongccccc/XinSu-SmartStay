#!/bin/bash
echo "=== 串口 ==="
ls /dev/ttyUSB* 2>/dev/null
echo
echo "=== 后端 ==="
systemctl is-active zhikong-backend
echo
echo "=== 屏幕 ==="
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
pgrep -c -f '[c]hromium.*8080' | sed 's/^/chromium 进程: /'
echo
echo "=== 门锁板 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hh.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hh.json'))
    print("  lock:", d.get('lock'))
    print("  rfid:", d.get('rfid'))
except Exception as e:
    print("  健康接口不可用:", e)
PY
