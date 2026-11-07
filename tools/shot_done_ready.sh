#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

# 办一次入住到完成页
curl -s -X POST $B/api/cancel > /dev/null; sleep 0.8
curl -s -X POST $B/api/session/start > /dev/null; sleep 0.4
curl -s -X POST $B/api/idcard/mock > /dev/null; sleep 0.4
curl -s -X POST -H 'Content-Type: application/json' -d '{"capture":false}' $B/api/face > /dev/null; sleep 0.3
curl -s -X POST $B/api/room/8801 > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"code":"TESTPAY"}' $B/api/pay > /dev/null; sleep 0.3
curl -s -X POST -H 'Content-Type: application/json' -d '{"uid":"CARD8801"}' $B/api/card > /dev/null
sleep 5
grim /tmp/done_ready.png && echo "截图完成"

# 恢复真实门锁配置
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p)); d['devices']['lock']['transport']='board'
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("已切回 board")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 8
echo "门锁传输: $(curl -s $B/api/health | python3 -c 'import sys,json;print((json.load(sys.stdin).get("lock") or {}).get("transport"))')"
