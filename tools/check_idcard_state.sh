#!/bin/bash
curl -s -m 6 http://127.0.0.1:8080/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
print("idcard:", d.get("idcard"))
print("lock  :", d.get("lock"))
PY
echo "--- 后端日志（最近）---"
tail -8 /opt/zhikong/logs/backend.out
echo "--- 身份证 WebAPI 探测频率（10 秒内错误次数）---"
before=$(grep -c "idcard" /opt/zhikong/logs/backend.out 2>/dev/null || echo 0)
sleep 10
after=$(grep -c "idcard" /opt/zhikong/logs/backend.out 2>/dev/null || echo 0)
echo "10 秒内新增日志行: $((after - before))（应为 0，说明服务离线不刷屏）"
