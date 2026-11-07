#!/bin/bash
B=http://127.0.0.1:8080
PB=123456

# 临时 mock 门锁，跑完整流程
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='mock'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 8

echo "=== 入住前房间状态 ==="
curl -s $B/api/home | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('  light=%s fan=%s' %(d['light'],d['fan']))"

curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8804 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8804"}' $B/api/card > /dev/null
sleep 6

echo "=== 入住完成后（应为迎宾模式：灯亮 + 风扇 30）==="
curl -s $B/api/home | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('  light=%s fan=%s' %(d['light'],d['fan']))"

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "开门码: $CODE"

echo "=== 凭码退房 ==="
curl -s -X POST -H 'Content-Type: application/json' -d "{\"pin\":\"$CODE\"}" $B/api/checkout | head -c 120
echo
sleep 3

echo "=== 退房后（应为节能模式：全关）==="
curl -s $B/api/home | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print('  light=%s fan=%s' %(d['light'],d['fan']))"

echo "=== 审计记录 ==="
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for k, p in c.execute("SELECT kind,payload FROM audit WHERE kind='room_mode' ORDER BY id DESC LIMIT 3"):
    print("  ", k, p)
c.close()
PY

# 恢复
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='board'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("已切回 board")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 6
