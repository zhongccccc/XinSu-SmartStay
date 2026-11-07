#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 1. 设备状态 ==="
curl -s $B/api/health > /tmp/q1.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/q1.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板: port=%s online=%s mock=%s fw=%s" % (
    lk.get('port'), lk.get('online'), lk.get('mock'), lk.get('firmware')))
print("  家居板:", hm.get('port'), hm.get('online'))
print("  读卡器:", rf.get('port'), rf.get('online'), "reads=", rf.get('reads'))
PY

echo
echo "=== 2. 在住订单 / 开门码 ==="
curl -s $B/api/state > /tmp/q2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/q2.json'))
except Exception as e:
    print("  state:", e); raise SystemExit
print("  step=%s" % d.get('step'))
ins = d.get('inhouse') or []
print("  在住 %d 单" % len(ins))
for o in ins[:5]:
    print("    %-6s 卡=%-12s 码=%s" % (o.get('room'), o.get('card_uid'), o.get('lock_code')))
if ins:
    open('/tmp/q_code.txt','w').write(str(ins[0].get('lock_code') or ''))
PY

CODE=$(cat /tmp/q_code.txt 2>/dev/null)
if [ -z "$CODE" ]; then echo "!! 没有开门码（可能没办入住）"; exit 0; fi

echo
echo "=== 3. 板子上校验 $CODE ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -8
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
