#!/bin/bash
B=http://127.0.0.1:8080
F=/opt/zhikong/face/samples

echo "=== 摄像头状态 ==="
curl -s $B/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
c = d.get('camera') or {}
print('  camera:', c.get('ok'), c.get('mode'))
"

echo
echo "=== 用真实摄像头 + 样例证件照 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"real\":true,\"idphoto\":\"$F/id_photo_sample.png\"}" \
  $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%s' % d.get('step'))
print('  结论=%s 分数=%s 耗时=%sms 帧数=%s' % (f.get('decision'), f.get('score'), f.get('ms'), f.get('frames')))
print('  原因=%s' % (f.get('reason') or '-'))
"
curl -s -X POST $B/api/cancel > /dev/null
