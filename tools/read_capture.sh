#!/bin/bash
echo "=== 身份证抓包结果 ==="
cat /opt/zhikong/data/idcap.out 2>/dev/null | head -30
echo
echo "=== 扫码结果（后端日志）==="
grep -i "\[hid\]" /opt/zhikong/logs/backend.out | tail -10
echo
echo "=== 审计（scan 事件）==="
curl -s http://127.0.0.1:8080/api/audit > /tmp/aud.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/aud.json'))
for a in d['items'][:8]:
    print(a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:120])
PY
