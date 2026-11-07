#!/bin/bash
PB=123456
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d.setdefault('devices', {})
d['devices']['camera_disabled'] = True
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("camera_disabled = True")
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 16

echo "=== 状态 ==="
curl -s -o /dev/null -w 'backend HTTP %{http_code}\n' http://127.0.0.1:8080/api/health
curl -s http://127.0.0.1:8080/api/health > /tmp/hc.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hc.json'))
except Exception:
    print("  health 读不到"); raise SystemExit
c = d.get('camera') or {}
lk = d.get('lock') or {}
print("  camera:", {k: c.get(k) for k in ('ok', 'mode', 'device') if k in c})
print("  lock  :", lk.get('port'), lk.get('online'), lk.get('firmware'))
PY
echo
echo "=== 负载（应明显下降）==="
uptime
echo
echo "=== 摄像头报错是否停了 ==="
echo "$PB" | sudo -S -p '' journalctl -b -n 6 --no-pager 2>/dev/null | grep -i 'isp\|cam_' | tail -4 || echo "  没有新的 ISP 报错了"
