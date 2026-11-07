#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 1. 开始入住（进入 ident 步骤）==="
curl -s -X POST $B/api/cancel > /dev/null
curl -s -X POST $B/api/session/start > /dev/null
sleep 0.6
curl -s $B/api/state | python3 -c "import sys,json;print('step=',json.load(sys.stdin)['step'])"

echo "=== 2. 模拟 Windows 桥推一张证 ==="
curl -s -X POST -H 'Content-Type: application/json' \
  -d "$(printf '{"name":"%s","idno":"440305199203182418"}' "$(printf '\351\231\210\346\200\235\350\277\234')")" \
  $B/api/idcard/inject
echo
sleep 0.8
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('step=',d['step'],'guest=',d.get('guest'),'idno=',d.get('idno'))"
curl -s -X POST $B/api/cancel > /dev/null
