#!/bin/bash
echo "=== 读卡器状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq7.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq7.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
rf = d.get('rfid') or {}
print("  port=%s online=%s reads=%s last=%s" % (
    rf.get('port'), rf.get('online'), rf.get('reads'), rf.get('last_uid')))
PY

echo
echo "=== 最近刷卡记录 ==="
grep -a '\[rfid\] card uid' /opt/zhikong/logs/backend.log | tail -3
echo "  现在: $(date '+%H:%M:%S')"

echo
echo "=== 当前流程 ==="
curl -s http://127.0.0.1:8080/api/state > /tmp/sq7.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/sq7.json'))
except Exception as e:
    print("  state:", e); raise SystemExit
print("  step=%s  msg=%s" % (d.get('step'), (d.get('msg') or '')[:40]))
PY

echo
echo "=== rfid 线程是否在跑 ==="
echo 123456 | sudo -S -p '' ls -l /proc/$(pgrep -f 'backend.main' | head -1)/fd 2>/dev/null | grep -c ttyUSB
echo "  （上面数字 > 0 说明后端还占着串口）"
