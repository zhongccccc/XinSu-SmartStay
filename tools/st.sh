#!/bin/bash
curl -s http://127.0.0.1:8080/api/state > /tmp/st.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/st.json'))
print("step:", d.get('step'), " 在住订单:", len(d.get('inhouse') or []))
for o in (d.get('inhouse') or [])[:5]:
    print("  ", o.get('room'), o.get('guest'), o.get('lock_code'))
PY
