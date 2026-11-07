#!/bin/bash
B=http://127.0.0.1:8080
F=/opt/zhikong/face/samples

run() {
  local id="$1"; shift
  local lives="$1"; shift
  curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
  curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
  curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "{\"real\":true,\"idphoto\":\"$F/$id\",\"livefiles\":[$lives]}" \
    $B/api/face | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  step=%-6s 结论=%-6s 分数=%-6s 耗时=%-6s 帧数=%s' % (
    d.get('step'), f.get('decision'), f.get('score'), f.get('ms'), f.get('frames')))
"
}

echo "=== 3 帧同人（现场照重复 3 次模拟连拍）==="
run id_photo_sample.png "\"$F/live_sim.jpg\",\"$F/live_sim.jpg\",\"$F/live_sim.jpg\""

echo "=== 1 帧（对比：应 retry）==="
run id_photo_sample.png "\"$F/live_sim.jpg\""

curl -s -X POST $B/api/cancel > /dev/null
