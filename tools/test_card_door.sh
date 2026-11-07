#!/bin/bash
B=http://127.0.0.1:8080

echo "=== 1. 办入住（绑定房卡 CARD8808）==="
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8808 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 4
curl -s -X POST $B/api/reset > /dev/null   # 回待机但保留凭证
sleep 1.5

echo "=== 2. 在待机状态下刷房卡（模拟读卡器）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8808"}' $B/api/card > /dev/null
sleep 3

echo "=== 3. 刷一张无效卡 ==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"DEADBEEF"}' $B/api/card > /dev/null
sleep 2

echo
echo "=== 门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -10
