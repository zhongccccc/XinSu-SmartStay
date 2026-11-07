#!/bin/bash
PB=123456
echo "=== 去掉写死的端口，让开机自动认领 ==="
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
dev = d.setdefault('devices', {})
dev.pop('home_port', None)        # 不再写死，交给开机扫描
dev['home_sim'] = False
dev['lock']['transport'] = 'auto'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("devices =", json.dumps({k: v for k, v in dev.items() if k in ('home_port', 'home_sim', 'lock')}, ensure_ascii=False))
PY

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 22

echo "=== 设备状态 ==="
curl -s http://127.0.0.1:8080/api/health > /tmp/hq4.json 2>/dev/null
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/hq4.json'))
except Exception as e:
    print("  health:", e); raise SystemExit
lk = d.get('lock') or {}; hm = d.get('home') or {}
print("  lock :", lk.get('port'), lk.get('online'), lk.get('firmware'))
print("  home :", hm.get('port'), hm.get('online'), hm.get('firmware'))
PY
echo
curl -s http://127.0.0.1:8080/api/home | head -c 240
echo
