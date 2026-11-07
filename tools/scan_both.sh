#!/bin/bash
PB=123456
echo "=== 直接扫一遍两个协议 ==="
echo "$PB" | sudo -S -p '' python3 /tmp/p115.py
echo
sleep 15
echo "=== 后端状态（等自动重连） ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq3.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq3.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'), "mock=", lk.get('mock'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
grep -aE '\[lock:board\]|\[port\]' /opt/zhikong/logs/backend.log | tail -4
