#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 当前在住 ==="
curl -s $B/api/state > /tmp/last.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/last.json'))
except Exception:
    print("  读不到"); raise SystemExit
ins = d.get('inhouse') or []
print("  共 %d 单" % len(ins))
for o in ins[:12]:
    print("    %-6s 码=%s" % (o.get('room'), o.get('lock_code')))
# 取最新一单
if ins:
    o = ins[0]
    open('/tmp/one_room.txt','w').write(str(o.get('room')))
    open('/tmp/one_code.txt','w').write(str(o.get('lock_code')))
    print("  选这单测试: 房间 %s 码 %s" % (o.get('room'), o.get('lock_code')))
PY

ROOM=$(cat /tmp/one_room.txt 2>/dev/null)
CODE=$(cat /tmp/one_code.txt 2>/dev/null)

echo
echo "=== 清空板上凭证，只写这一条 ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send.py \
  "zk revoke" \
  "zk issue $ROOM $CODE - 1440" \
  "zk code $CODE" 2>&1 | head -14
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
echo
echo ">>> 去门锁板键盘输入: $CODE 然后按 #"
