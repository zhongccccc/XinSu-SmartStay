#!/bin/bash
PB=123456
DEST=/opt/zhikong/app/assets/voice

echo "=== 安装音频 ==="
mkdir -p /tmp/voice 2>/dev/null
echo "$PB" | sudo -S -p '' mkdir -p "$DEST"
echo "$PB" | sudo -S -p '' cp -f /tmp/voice/*.wav "$DEST"/ 2>/dev/null || cp -f /tmp/voice/*.wav "$DEST"/
echo "$PB" | sudo -S -p '' chown -R root:root "$DEST" 2>/dev/null
ls "$DEST"/*.wav | wc -l | sed 's/^/  音频文件数: /'

echo
echo "=== 重启后端 ==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -o /dev/null -w '  HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

echo
echo "=== 播一句（欢迎语，应听到正常中文）==="
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 7
echo "  已发送"
