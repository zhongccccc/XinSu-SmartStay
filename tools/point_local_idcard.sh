#!/bin/bash
cat > /opt/zhikong/etc/config.json <<'EOF'
{
  "devices": {
    "scanner_name_re": "(?i)(barcode|bar code|scanner|scan|扫码|二维码|qr|usbscn|scn|rfid|reader|读卡|ic card|id card|pos)"
  },
  "idcard": {
    "mode": "webapi",
    "url": "http://127.0.0.1:7846",
    "interval": 0.4,
    "timeout": 20
  },
  "rfid": { "enabled": true, "transport": "serial", "port": "/dev/ttyUSB0", "baud": 9600 }
}
EOF
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 2
curl -s -m 8 http://127.0.0.1:8080/api/health > /tmp/hid.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/hid.json'))
print("idcard:", d.get("idcard"))
PY
