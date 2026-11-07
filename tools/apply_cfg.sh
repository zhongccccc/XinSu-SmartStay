#!/bin/bash
PB=123456
cat > /opt/zhikong/etc/config.json <<'EOF'
{
  "devices": {
    "scanner_name_re": "(?i)(barcode|bar code|scanner|scan|扫码|二维码|qr|usbscn|scn|rfid|reader|读卡|ic card|id card|pos)"
  }
}
EOF
echo "config written"
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3

echo
echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/devices > /tmp/dev.json
python3 -c "
import json
d=json.load(open('/tmp/dev.json'))
for i in d['items']: print('%-8s %-6s %s' % (i['key'], i['present'], i['detail']))
print('scanner devices:', d.get('input') and [(x['name'],x['has_abs']) for x in d['input']])
"
echo
echo "=== HID 抓取日志 ==="
grep -i "hid" /opt/zhikong/logs/backend.out | tail -6
