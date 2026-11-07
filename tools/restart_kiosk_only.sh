#!/bin/bash
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 14
echo "界面进程: $(pgrep -c -f 'chromium.*8080')"
curl -s http://127.0.0.1:8080/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
c = d.get('camera') or {}
print('camera ok =', c.get('ok'))
PY
