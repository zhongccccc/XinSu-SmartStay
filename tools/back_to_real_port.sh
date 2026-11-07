#!/bin/bash
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock'].update({"transport": "auto", "port": "/dev/ttyUSB1"})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("lock =", d['devices']['lock'])
PY
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -2
sleep 3
curl -s http://127.0.0.1:8080/api/health | python3 -c "
import sys, json
print('  ', json.load(sys.stdin).get('lock'))
"
