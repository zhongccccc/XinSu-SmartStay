#!/bin/bash
B=http://127.0.0.1:8080

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.6
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4

for i in $(seq 1 8); do
  OUT=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"real":true,"frames":3}' $B/api/face)
  echo "$OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('face') or {}
print('  [第 $i 次] 结论=%-6s 分数=%-6s 耗时=%-5s 帧=%s 原因=%s' % (
    f.get('decision'), f.get('score'), f.get('ms'), f.get('frames'), f.get('reason') or '-'))
"
  DEC=$(echo "$OUT" | python3 -c "import sys,json;print((json.load(sys.stdin).get('face') or {}).get('decision') or '')")
  if [ "$DEC" = "pass" ]; then echo "  ==> 比对通过"; break; fi
  # 没检测到脸就再等，让用户就位
  sleep 2
done
curl -s -X POST $B/api/cancel > /dev/null
echo "结束"
