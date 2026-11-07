#!/bin/bash
PB=123456
# 收尾：停掉 qemu 读卡服务，恢复系统正常状态
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f "strace -f" 2>/dev/null
sleep 1
echo "=== 残留进程 ==="
pgrep -af "qemu-aarch64|strace" | head -5 || echo "none"
echo "=== 后端 ==="
systemctl is-active zhikong-backend
echo "=== 读卡服务端口 ==="
ss -ltnp 2>/dev/null | grep -E "7846" || echo "已停止"
echo "=== 设备状态 ==="
curl -s -m 6 http://127.0.0.1:8080/api/devices > /tmp/dv.json
python3 - <<'PY'
import json
d = json.load(open('/tmp/dv.json'))
print(" | ".join("%s:%s" % (i['key'], 'ON' if i['present'] else '--') for i in d['items']))
PY
echo "=== 日志：libusb 枚举 ==="
wc -l /tmp/libusb.log 2>/dev/null || echo none
grep -icE "new device|device list" /tmp/libusb.log 2>/dev/null || true
