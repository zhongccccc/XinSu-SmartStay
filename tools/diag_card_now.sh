#!/bin/bash
echo "=== 设备 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hv.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hv.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}; rf = d.get('rfid') or {}
print("  门锁板:", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  家居板:", hm.get('port'), hm.get('online'), hm.get('firmware'))
print("  读卡器:", rf.get('port'), "online=", rf.get('online'), "reads=", rf.get('reads'), "last=", rf.get('last_uid'))
PY

echo
echo "=== 读卡器最近读到卡的时间 ==="
grep -a '\[rfid\] card uid' /opt/zhikong/logs/backend.log | tail -5
echo "  当前时间: $(date '+%H:%M:%S')"

echo
echo "=== 最近刷卡事件（card_door / card） ==="
grep -aE 'card_door|card uid|绑定|CARDBIND' /opt/zhikong/logs/backend.log | tail -6

echo
echo "=== 当前流程状态 ==="
curl -s http://127.0.0.1:8080/api/state | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('   step=%s msg=%s' % (d.get('step'), (d.get('msg') or '')[:40]))
print('   在住订单=%d' % len(d.get('inhouse') or []))
"
