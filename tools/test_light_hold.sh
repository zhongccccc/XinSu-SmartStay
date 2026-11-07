#!/bin/bash
B=http://127.0.0.1:8080
show() { curl -s $B/api/home | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
print('   t=%ss 灯=%s 风扇=%s 人体=%s' % ('$1', d.get('light'), d.get('fan'), d.get('pir')))
"; }

echo "=== 开灯（宿主机命令）==="
curl -s -X POST -H 'Content-Type: application/json' -d '{"on":true}' $B/api/home/light > /dev/null
sleep 1;  show 1s
sleep 4;  show 5s
sleep 4;  show 9s
