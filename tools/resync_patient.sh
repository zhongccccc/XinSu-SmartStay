#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

echo "=== 等后端就绪（最多 90 秒）==="
READY=0
for i in $(seq 1 90); do
  if curl -s -m 1 -o /dev/null $B/api/health 2>/dev/null; then READY=1; echo "  就绪（${i}s）"; break; fi
  sleep 1
done
if [ "$READY" = "0" ]; then echo "!! 后端 90 秒内没起来"; exit 1; fi

echo
echo "=== 在住订单 ==="
curl -s $B/api/state > /tmp/r_ct.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/r_ct.json'))
ins = d.get('inhouse') or []
print("  step=%s 在住=%d" % (d.get('step'), len(ins)))
for o in ins[:5]:
    print("    %-6s 卡=%-12s 码=%s" % (o.get('room'), o.get('card_uid'), o.get('lock_code')))
if ins:
    open('/tmp/r_code.txt','w').write(str(ins[0].get('lock_code') or ''))
PY

echo
echo "=== 重新下发凭证 ==="
curl -s -X POST $B/api/lock/resync | head -c 400
echo

CODE=$(cat /tmp/r_code.txt 2>/dev/null)
echo
echo "=== 板上校验 $CODE ==="
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 2
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py "zk code $CODE" 2>&1 | head -8
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
