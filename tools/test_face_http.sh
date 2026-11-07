#!/bin/bash
B=http://127.0.0.1:8080
F=/opt/zhikong/face/samples

echo "=== 开始一次入住到人脸页 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.5
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.5
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=%s'%d.get('step'))"

echo
echo "=== 真实比对（同人样例）==="
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"real\":true,\"idphoto\":\"$F/id_photo_sample.png\",\"livefiles\":[\"$F/live_sim.jpg\"]}" \
  $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%s' % d.get('step'))
print('  结论=%s 分数=%s 耗时=%sms 帧数=%s' % (f.get('decision'), f.get('score'), f.get('ms'), f.get('frames')))
print('  原因=%s' % (f.get('reason') or '-'))
"

echo
echo "=== 换一张不同的人（应为低分/失败）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"real\":true,\"idphoto\":\"$F/id_photo_sample.png\",\"livefiles\":[\"$F/webcam_live.jpg\"]}" \
  $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%s' % d.get('step'))
print('  结论=%s 分数=%s 耗时=%sms' % (f.get('decision'), f.get('score'), f.get('ms')))
print('  原因=%s' % (f.get('reason') or '-'))
"

echo
echo "=== 清理 ==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 1
grep -a '\[face\] 结论' /opt/zhikong/logs/backend.log | tail -3
