#!/bin/bash
sleep 8
echo "=== 服务状态 ==="
systemctl is-active idreader.service
systemctl status idreader.service --no-pager 2>&1 | head -12
echo
echo "=== 7846 ==="
ss -ltnp 2>/dev/null | grep 7846 || echo "未监听"
echo
echo "=== 日志 ==="
tail -15 /opt/zhikong/logs/idreader.out 2>/dev/null
echo
echo "=== 读卡 ==="
curl -s -m 8 "http://127.0.0.1:7846/api/readCard?utf8=1"
echo
