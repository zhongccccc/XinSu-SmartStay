#!/bin/bash
B=http://127.0.0.1:8080
F=/opt/zhikong/face/samples

curl -s -X POST $B/api/cancel > /dev/null; sleep 1
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4

BODY=$(printf '{"real":true,"idphoto":"%s/id_photo_sample.png","livefiles":["%s/live_sim.jpg"]}' "$F" "$F")

echo "--- 请求体 ---"
echo "$BODY"
echo "--- 原始响应（前 400 字节）---"
curl -s -X POST -H 'Content-Type: application/json' -d "$BODY" $B/api/face | head -c 400
echo
echo "--- 后端日志尾部 ---"
tail -30 /opt/zhikong/logs/backend.out | grep -a -iE 'face|error|traceback|exception' | tail -10
