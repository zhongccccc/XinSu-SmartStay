#!/bin/bash
echo "=== 一体机读卡器状态（刷完卡后再看）==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hr.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hr.json'))
print("  rfid:", d.get('rfid'))
PY
echo
echo "=== 最近的刷卡记录 ==="
echo 123456 | sudo -S -p '' python3 - <<'PY'
import sqlite3, json
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
for kind, payload in c.execute("SELECT kind, payload FROM audit WHERE kind='scan' ORDER BY id DESC LIMIT 3"):
    print("  scan:", payload)
c.close()
PY
