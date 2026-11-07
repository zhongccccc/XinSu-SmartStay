#!/bin/bash
# 切换家居板：真实 / 模拟
set -e
MODE="${1:-real}"
python3 - "$MODE" <<'PY'
import json, sys
mode = sys.argv[1]
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {})
d['devices']['home_sim'] = (mode == 'sim')
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("home_sim =", d['devices']['home_sim'])
PY
echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
sleep 10
curl -s http://127.0.0.1:8080/api/home
echo
