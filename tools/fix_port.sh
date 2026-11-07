#!/bin/bash
PB=123456
python3 - <<'PY'
import json
p='/opt/zhikong/etc/config.json'
d=json.load(open(p))
d['devices']['lock'].update({"transport":"board","port":"/dev/ttyUSB2","baud":115200})
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print("配置:", d['devices']['lock'])
PY
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 7
curl -s http://127.0.0.1:8080/api/health > /tmp/h5.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/h5.json'))
print("lock:", d.get('lock'))
PY
