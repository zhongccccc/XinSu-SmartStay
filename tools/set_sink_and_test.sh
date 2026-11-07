#!/bin/bash
echo "=== 把默认输出切到 USB 音箱 ==="
ID=$(wpctl status 2>/dev/null | grep -i 'USB Composite' | grep -oE '[0-9]+\.' | head -1 | tr -d '.')
echo "  USB sink id = $ID"
if [ -n "$ID" ]; then
  wpctl set-default "$ID" && echo "  已设为默认"
  wpctl status 2>/dev/null | sed -n '/Sinks/,/Sources/p' | head -6
fi

echo
echo "=== 重启后端 ==="
echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -o /dev/null -w '  HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

echo
echo "=== 播一句欢迎语（应从小音箱出声）==="
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 6
echo "  完成"
