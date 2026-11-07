#!/bin/bash
export ZHIKONG_HOME=/opt/zhikong
echo "--- devices ---"
curl -s -m 8 http://127.0.0.1:8080/api/devices > /tmp/dev.json
python3 -c "
import json
d = json.load(open('/tmp/dev.json'))
for i in d['items']:
    print('%-10s %-6s %s' % (i['key'], i['present'], i['detail']))
print('inputs:', [(x['name'], x['has_abs']) for x in d['input']][:6])
print('usb:', [(u['id'], u['product']) for u in d['usb']])
"
