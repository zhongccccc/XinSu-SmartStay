#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" 2>&1 | tail -1; sleep 1.2; }

echo "=== 点『开灯』(106,370) ==="
tap 106 370
sleep 2
echo "=== 点击命中 ==="
grep -E "\[ui\]" /opt/zhikong/logs/backend.out | tail -3
echo "=== 语音审计（最近 3 条）==="
curl -s http://127.0.0.1:8080/api/audit > /tmp/a.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/a.json'))
n = 0
for a in d['items']:
    if a['kind'] == 'voice':
        print("  ", json.dumps(a['payload'], ensure_ascii=False)[:80])
        n += 1
        if n >= 3:
            break
PY
grim /tmp/voice_fixed2.png && echo shot ok
