#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 当前状态 ==="
curl -s $B/api/state | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  step =', d.get('step'), '|', d.get('step_label'))
print('  msg  =', (d.get('msg') or '')[:60])
print('  guest=', d.get('guest'))
"
echo
echo "=== 摄像头 ==="
curl -s $B/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
c = d.get('camera') or {}
print('  ', {k: c.get(k) for k in ('ok','device','pipeline','error') if k in c})
"
echo
echo "=== 最近日志（camera/face/error）==="
grep -aEi 'camera|face|error|Traceback' /opt/zhikong/logs/backend.log | tail -12
echo
echo "=== 进程 ==="
ps -u shiqi -o pid,pcpu,etime,cmd --sort=-pcpu 2>/dev/null | head -6
echo
echo "=== 摄像头设备占用 ==="
echo 123456 | sudo -S -p '' fuser -v /dev/video* 2>&1 | head -6
