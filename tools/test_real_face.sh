#!/bin/bash
B=http://127.0.0.1:8080

echo "=== 用最新证件照 + 真实摄像头做比对 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4

curl -s -X POST -H 'Content-Type: application/json' -d '{"real":true,"frames":3}' \
  $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%s' % d.get('step'))
print('  结论=%s  分数=%s  耗时=%sms  帧数=%s' % (
    f.get('decision'), f.get('score'), f.get('ms'), f.get('frames')))
print('  原因=%s' % (f.get('reason') or '-'))
"

echo
echo "=== 后端日志 ==="
grep -aF '[face]' /opt/zhikong/logs/backend.log | tail -3
