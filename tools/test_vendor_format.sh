#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 启动假厂商服务（真实返回结构）==="
pkill -f fake_vendor_7846 2>/dev/null
pkill -f fake_idcard_service 2>/dev/null
sleep 1
nohup python3 /tmp/fake_vendor_7846.py > /tmp/fv.out 2>&1 &
sleep 2
curl -s -m 4 "http://127.0.0.1:7846/api/readCard?utf8=1" | head -c 200; echo
echo
echo "=== 用 K1 自己的解析器读一次 ==="
python3 /opt/zhikong/app/backend/devices/idcard_web.py http://127.0.0.1:7846 2>&1 | head -20
echo
echo "=== 走业务流程 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null
sleep 3.5
curl -s $B/api/state | python3 - <<'PY'
import sys, json
d = json.load(sys.stdin)
print("step=%s guest=%s idno=%s sex=%s nation=%s addr=%s" % (
    d['step'], d.get('guest'), d.get('idno'), '', '', ''))
PY
curl -s $B/api/audit | python3 -c "
import sys,json
d=json.load(sys.stdin)
for a in d['items'][:3]:
    print(a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:100])
"
pkill -f fake_vendor_7846 2>/dev/null
curl -s -X POST $B/api/cancel > /dev/null
