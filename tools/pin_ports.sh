#!/bin/bash
PB=123456
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {})
d['devices']['home_port'] = '/dev/ttyUSB2'
d['devices']['home_sim'] = False
d['devices'].setdefault('lock', {})
d['devices']['lock']['transport'] = 'board'
d['devices']['lock']['port'] = '/dev/ttyUSB1'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("config 已固定端口:", d['devices']['lock']['port'], d['devices']['home_port'])
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
tr -d '\r' < /tmp/sc.sh | bash
