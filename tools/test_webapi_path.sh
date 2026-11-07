#!/bin/bash
B=http://127.0.0.1:8080
st() { curl -s -m 5 $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=%s guest=%s idno=%s' % (d['step'], d.get('guest'), (d.get('idno') or '')[:6]))"; }

echo "=== 复位并开始入住 ==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null
sleep 1
st

echo "=== 启动假读卡服务 ==="
pkill -f fake_idcard_service 2>/dev/null
nohup python3 /tmp/fake_idcard_service.py > /tmp/fake.out 2>&1 &
sleep 4
st

echo "=== 后端日志 ==="
grep -E "idcard" /opt/zhikong/logs/backend.out | tail -3

echo "=== 停掉假服务 ==="
pkill -f fake_idcard_service 2>/dev/null
sleep 2
curl -s -X POST $B/api/cancel > /dev/null
st
