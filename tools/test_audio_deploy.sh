#!/bin/bash
cd /opt/zhikong/app || exit 1
echo "=== 选中的声卡 ==="
python3 - <<'PY'
import sys
sys.path.insert(0, '/opt/zhikong/app')
from backend.devices.audio import CARD
print('  CARD =', CARD)
PY

echo
echo "=== 重启后端 ==="
echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -o /dev/null -w '  HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

echo
echo "=== 播报测试：欢迎语 ==="
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 4
grep -a 'audio' /opt/zhikong/logs/backend.log | tail -3
