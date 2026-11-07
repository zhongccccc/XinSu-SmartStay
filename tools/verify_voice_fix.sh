#!/bin/bash
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
B=http://127.0.0.1:8080
tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1; sleep 1.2; }

echo "=== 重载 kiosk（加载新 app.js）==="
pkill -f "[c]hromium.*8080"; sleep 1
nohup /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
sleep 13

curl -s -X POST $B/api/cancel > /dev/null
sleep 1
echo "=== 打开语音面板 + 点『开灯』 ==="
tap 731 24
tap 107 400
sleep 2.5
grim /tmp/voice_fixed.png && echo "shot ok"
echo "=== 后端 voice 事件 ==="
grep -E "\[voice\]" /opt/zhikong/logs/backend.out | tail -2
curl -s $B/api/audit | python3 -c "
import sys,json
d=json.load(sys.stdin)
for a in d['items'][:3]:
    print(' ', a['kind'], json.dumps(a['payload'], ensure_ascii=False)[:70])
"
