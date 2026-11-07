#!/bin/bash
# 全流程自动化冒烟测试（无硬件，走模拟接口）
B=http://127.0.0.1:8080
j() { python3 -c "import sys,json;d=json.load(sys.stdin);print(eval(sys.argv[1]))" "$1"; }

echo "== 1. 开始 =="
curl -s -X POST $B/api/session/start | j 'd["step"], d["msg"]'
echo "== 2. 模拟身份证 =="
curl -s -X POST $B/api/idcard/mock | j 'd["step"], d["guest"], d["msg"]'
echo "== 3. 人脸 =="
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":true}' $B/api/face | j 'd["step"], d["face"], d["msg"]'
echo "== 4. 选房 8801 =="
curl -s -X POST $B/api/room/8801 | j 'd["step"], d["room"]["no"], d["price"], d["msg"]'
echo "== 5. 扫码支付 =="
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"2845120099887766"}' $B/api/pay | j 'd["step"], d["msg"]'
echo "== 6. 房卡 =="
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"A1B2C3D4"}' $B/api/card | j 'd["step"], d["card_uid"], d["msg"]'
echo "== 7. 下发门锁 =="
curl -s -X POST $B/api/issue | j 'd["step"], d["lock_code"], d["order_id"], d["msg"]'
echo "== 8. 语音指令 =="
curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"帮我送一双拖鞋"}' $B/api/voice | j 'd["reply"]'
curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"退房时间是几点"}' $B/api/voice | j 'd["reply"]'
echo "== 9. 门锁开门 =="
curl -s -X POST -H 'Content-Type: application/json' -d '{"room":"8801","method":"card"}' $B/api/lock/open
echo
echo "== 10. 工单 =="
curl -s $B/api/workorders | j '[(w["id"],w["room"],w["text"],w["status"]) for w in d["items"][:5]]'
echo "== 11. 审计 =="
curl -s $B/api/audit | j '[(a["kind"]) for a in d["items"][:12]]'
echo "== 12. 设备 =="
curl -s $B/api/devices | j '[(i["key"],i["present"]) for i in d["items"]]'
echo "== 13. 复位 =="
curl -s -X POST $B/api/cancel | j 'd["step"]'
