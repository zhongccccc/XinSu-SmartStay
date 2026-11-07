#!/bin/bash
B=http://127.0.0.1:8080
curl -s -X POST $B/api/cancel > /dev/null
python3 - <<'PY'
import sqlite3
c = sqlite3.connect('/opt/zhikong/data/zhikong.db')
c.execute("DELETE FROM workorders")
c.execute("DELETE FROM audit WHERE kind IN ('voice','idcard','face')")
c.commit()
print("工单已清，剩余 audit:", c.execute("SELECT COUNT(*) FROM audit").fetchone()[0])
c.close()
PY
curl -s -m 5 $B/api/state | python3 -c "import sys,json;print('step =', json.load(sys.stdin)['step'])"
