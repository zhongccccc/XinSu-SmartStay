#!/bin/bash
# 安装后端为 systemd 服务（开机自启，崩溃自动重启）
set -e
PB='123456'
S="echo $PB | sudo -S -p ''"

pid=$(ss -ltnp 2>/dev/null | awk '/:8080 /{print $NF}' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
[ -n "$pid" ] && kill "$pid" 2>/dev/null && sleep 1 || true

echo "$PB" | sudo -S -p '' cp /opt/zhikong/app/deploy/zhikong-backend.service /etc/systemd/system/zhikong-backend.service
echo "$PB" | sudo -S -p '' systemctl daemon-reload
echo "$PB" | sudo -S -p '' systemctl enable zhikong-backend.service
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend.service
sleep 8
systemctl is-active zhikong-backend.service
curl -s -m 5 http://127.0.0.1:8080/api/health | head -c 300
echo
journalctl -u zhikong-backend -n 5 --no-pager | tail -5
