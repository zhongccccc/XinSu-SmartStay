#!/bin/bash
B=http://127.0.0.1:8080

echo "=== 流程状态 ==="
curl -s $B/api/state > /tmp/st.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/st.json'))
except Exception as e:
    print('  读不到:', e); raise SystemExit
print('  step=%s  guest=%s  idno=%s' % (d.get('step'), d.get('guest'), d.get('idno')))
PY

echo
echo "=== idcard 相关日志（最近 6 条）==="
grep -aF '[idcard]' /opt/zhikong/logs/backend.log | tail -6 || echo "  没有 [idcard] 日志"

echo
echo "=== 证件照目录 ==="
ls -lh /opt/zhikong/data/idphotos/ 2>/dev/null | tail -5 || echo "  目录不存在（说明没读到过带照片的卡）"

echo
echo "=== 直接问读卡器服务（请把身份证放在读卡区）==="
curl -s -m 6 'http://127.0.0.1:7846/api/readCard?utf8=1' > /tmp/card.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/card.json'))
except Exception as e:
    print('  响应不是 JSON:', e)
    print('  原始内容:', open('/tmp/card.json', encoding='utf-8', errors='ignore').read()[:300])
    raise SystemExit

print('  resultFlag=%s errorMsg=%s' % (d.get('resultFlag'), d.get('errorMsg')))
rc = d.get('resultContent') if isinstance(d.get('resultContent'), dict) else d
keys = sorted(rc.keys())
print('  返回字段(%d 个): %s' % (len(keys), ', '.join(keys[:25])))

# 找所有像照片的字段
found = []
for k, v in rc.items():
    if isinstance(v, str) and len(v) > 2000:
        head = v[:40].replace('\n', '')
        found.append((k, len(v), head))
    elif isinstance(v, (bytes, bytearray)):
        found.append((k, len(v), '<bytes>'))
if found:
    for k, n, head in found:
        print('  ★ 大字段 %s: %d 字符  开头=%s' % (k, n, head))
else:
    print('  ✗ 没有任何大字段（不像带照片）')
PY
