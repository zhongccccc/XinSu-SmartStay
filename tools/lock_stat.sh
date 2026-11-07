#!/bin/bash
curl -s http://127.0.0.1:8080/api/health > /tmp/hq3.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hq3.json'))
lk = d.get('lock') or {}
print("lock: transport=%s port=%s online=%s mock=%s" % (
    lk.get('transport'), lk.get('port'), lk.get('online'), lk.get('mock')))
PY
