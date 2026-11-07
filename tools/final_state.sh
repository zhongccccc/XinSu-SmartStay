#!/bin/bash
curl -s http://127.0.0.1:8080/api/health > /tmp/h.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/h.json'))
print("lock  :", d.get('lock'))
print("camera:", d['camera']['ok'], " rfid:", d['rfid']['online'], " idcard:", d['idcard']['online'])
PY
echo "--- 服务 ---"
systemctl is-active zhikong-backend idreader
echo "--- 文档 ---"
ls /opt/zhikong/docs/
