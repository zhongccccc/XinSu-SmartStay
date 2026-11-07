#!/bin/bash
curl -s http://127.0.0.1:8080/api/state > /tmp/sz.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/sz.json'))
print("step:", d.get('step'))
print("在住订单:", len(d.get('inhouse') or []))
PY
