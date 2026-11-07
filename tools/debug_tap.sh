#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080

echo "=== 当前状态 ==="
curl -s $B/api/state > /tmp/s.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/s.json'))
print("  step=%s guest=%s" % (d['step'], d.get('guest')))
PY

echo "=== 试拍一个确定存在的按钮（开始人脸核验 437,280）==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 437 280
sleep 1.5
grep -E "\[ui\]" /opt/zhikong/logs/backend.out | tail -2

echo "=== 试拍返回键 (645,24) ==="
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py 645 24
sleep 1.5
grep -E "\[ui\]" /opt/zhikong/logs/backend.out | tail -2

echo "=== 结果 ==="
curl -s $B/api/state > /tmp/s2.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/s2.json'))
print("  step=%s guest=%s" % (d['step'], d.get('guest')))
PY
grim /tmp/back_after2.png
