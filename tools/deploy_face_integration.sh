#!/bin/bash
PB=123456
set -e
cd /opt/zhikong/app
python3 -m py_compile backend/main.py backend/core/model.py backend/devices/idcard_web.py backend/devices/face_local.py
echo "COMPILE_OK"

echo "=== 打开真实比对（face_debug 便于无读卡器时测试）==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
k = d.setdefault('kiosk', {})
k['face_sim'] = False
k['face_debug'] = True
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print('face_sim=%s face_debug=%s' % (k['face_sim'], k['face_debug']))
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 22
curl -s -o /dev/null -w 'backend HTTP %{http_code}\n' http://127.0.0.1:8080/api/health
grep -a '\[face\]' /opt/zhikong/logs/backend.log | tail -3
