#!/bin/bash
B=http://127.0.0.1:8080
echo "=== 连读 12 次（约 24 秒）==="
ok=0
for i in $(seq 1 12); do
  r=$(curl -s -m 6 'http://127.0.0.1:7846/api/readCard?utf8=1')
  flag=$(echo "$r" | grep -o '"resultFlag" : "[0-9]*"' | grep -o '[0-9]*$')
  echo "  #$i flag=$flag"
  if [ "$flag" = "0" ]; then
    echo "$r" > /tmp/idcard_ok.json
    ok=1
    cat /tmp/idcard_ok.json
    break
  fi
  sleep 2
done
if [ "$ok" = "1" ]; then
  echo "=== 解析 ==="
  python3 - <<'PY'
import json
d = json.load(open('/tmp/idcard_ok.json'))
rc = d.get("resultContent") or {}
print("姓名:", rc.get("name"))
print("证号:", rc.get("idNum"))
print("性别:", {"1": "男", "2": "女"}.get(str(rc.get("gender")), rc.get("gender")))
print("民族码:", rc.get("nation"))
print("出生:", rc.get("birthday"))
print("住址:", rc.get("address"))
print("签发:", rc.get("issueOrg"))
print("照片长度:", len(rc.get("photo") or ""))
PY
else
  echo "=== 未读到卡 ==="
  journalctl -u idreader --no-pager -n 6 | tail -6
fi
