#!/bin/bash
B=http://127.0.0.1:8080
echo "backend: $(systemctl is-active zhikong-backend)"
curl -s -o /dev/null -w 'HTTP %{http_code}\n' $B/api/health
curl -s $B/api/state > /tmp/s.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/s.json'))
print('step =', d.get('step'))
print('guest =', d.get('guest'))
PY
echo "--- 最近比对记录 ---"
grep -aF '[face] 结论' /opt/zhikong/logs/backend.log | tail -4
