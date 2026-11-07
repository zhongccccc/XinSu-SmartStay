#!/bin/bash
PB=123456
echo "=== 恢复摄像头 ==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {})
d['devices']['camera_disabled'] = False
d['kiosk'] = d.get('kiosk') or {}
d['kiosk']['face_sim'] = True          # 不比对，但保留摄像头画面
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("camera_disabled = False, face_sim = True")
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 16

echo "=== 状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hf2.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hf2.json'))
except Exception:
    print("  health 读不到"); raise SystemExit
c = d.get('camera') or {}
lk = d.get('lock') or {}
hm = d.get('home') or {}
print("  camera:", {k: c.get(k) for k in ('ok', 'mode', 'device', 'fps') if k in c})
print("  lock  :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home  :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
echo
echo "=== 负载 ==="
uptime
