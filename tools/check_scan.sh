#!/bin/bash
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
echo "--- hid 抓取日志 ---"
grep -i "\[hid\]" /opt/zhikong/logs/backend.out | tail -6
echo "--- 设备状态 ---"
curl -s http://127.0.0.1:8080/api/devices > /tmp/dev.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/dev.json'))
for i in d['items']:
    print('%-8s %-6s %s' % (i['key'], i['present'], i['detail']))
PY
