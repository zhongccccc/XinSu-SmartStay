#!/bin/bash
# 在 K1 上起一个临时文件服务，把 board_app 里的文件发给 Ubuntu 虚拟机
PB=123456
pkill -f "http.server 8899" 2>/dev/null
sleep 0.5
cd /opt/zhikong/board_app || exit 1
setsid nohup python3 -m http.server 8899 --bind 0.0.0.0 > /tmp/httpd.log 2>&1 < /dev/null &
sleep 1.5
echo "=== 目录 ==="
ls -l /opt/zhikong/board_app/
echo "=== 端口 ==="
ss -ltnp 2>/dev/null | grep 8899 || echo "  未监听"
echo "=== 自测 ==="
curl -s -o /dev/null -w "  /zk_lock.c -> %{http_code}\n" http://127.0.0.1:8899/zk_lock.c
curl -s -o /dev/null -w "  /setup_zk_app.sh -> %{http_code}\n" http://127.0.0.1:8899/setup_zk_app.sh
