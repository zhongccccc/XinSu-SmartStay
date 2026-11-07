#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
echo "=== 服务 ==="
systemctl is-active zhikong-backend
echo "=== 设备健康 ==="
for i in $(seq 1 10); do
  curl -s -m 6 $B/api/health > /tmp/hb.json 2>/dev/null && break
  sleep 3
done
python3 - <<'PY'
import json
d = json.load(open('/tmp/hb.json'))
print("camera:", d.get("camera"))
print("rfid  :", d.get("rfid"))
print("idcard:", d.get("idcard"))
PY
echo "=== 快照 ==="
curl -s -m 8 -o /tmp/boot_snap.jpg -w '%{http_code} %{size_download}\n' $B/api/camera/snapshot.jpg
echo "=== 相机日志 ==="
grep -E "\[camera\]" /opt/zhikong/logs/backend.out | tail -4
echo "=== kiosk ==="
pgrep -c -f "[c]hromium.*8080"
