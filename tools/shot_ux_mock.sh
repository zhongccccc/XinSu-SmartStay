#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

# 临时切 mock
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p))
d['devices']['lock']['transport']='mock'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("已切到 mock")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 7

# 重启 kiosk 拉新前端
pkill -f 'chromium.*8080'; sleep 2
setsid nohup bash /opt/zhikong/app/scripts/app_launch.sh > /tmp/kiosk.log 2>&1 < /dev/null &
sleep 14

# 跑入住到完成页
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8806 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8806"}' $B/api/card > /dev/null
sleep 4
grim /tmp/ux_done2.png && echo "完成页截图"
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d.get('step'),'code=',d.get('lock_code'))"
