#!/bin/bash
echo "=== 当前 sink 列表 ==="
wpctl status 2>/dev/null | sed -n '/Sinks:/,/Sink endpoints/p'

# 从 Sinks 段里找 USB 的编号（行首数字，形如 "75. USB Composite"）
ID=$(wpctl status 2>/dev/null | sed -n '/Sinks:/,/Sink endpoints/p' | grep -i 'USB Composite' | sed -E 's/^[^0-9]*([0-9]+)\..*/\1/' | head -1)
echo "  USB sink id = $ID"
if [ -z "$ID" ]; then echo "  没找到 USB sink"; exit 1; fi

wpctl set-default "$ID"
echo "  设置结果:"
wpctl status 2>/dev/null | sed -n '/Sinks:/,/Sink endpoints/p'

echo
echo "=== 重启后端并播报 ==="
echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 6
echo "  播报已发送"
