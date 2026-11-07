#!/bin/bash
pkill -f 'user-data-dir=/tmp/chrome-co2' 2>/dev/null
pkill -f 'user-data-dir=/tmp/chrome-co' 2>/dev/null
rm -rf /tmp/chrome-co2 /tmp/chrome-co
sleep 1
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 12
echo "=== 实例数 ==="
pgrep -c -f 'chromium.*8080'
echo "=== 门锁状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hz10.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hz10.json'))
    lk = d.get('lock') or {}
    print("transport=%s online=%s" % (lk.get('transport'), lk.get('online')))
except Exception as e:
    print("health 读取失败:", e)
PY
