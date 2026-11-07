#!/bin/bash
B=http://127.0.0.1:8080
PB=123456
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0

# 恢复真实板卡传输
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock']['transport'] = 'board'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("已切回 board")
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 7

# 清订单 + 回待机
echo "$PB" | sudo -S -p '' python3 /tmp/coa.py 2>&1 | tail -1
curl -s -X POST $B/api/reset > /dev/null
sleep 2
grim /tmp/idle_now.png && echo "待机页截图完成"
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 5
curl -s $B/api/health > /tmp/hf9.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hf9.json'))
lk = d.get('lock') or {}
print("lock: transport=%s online=%s mock=%s" % (lk.get('transport'), lk.get('online'), lk.get('mock')))
PY
