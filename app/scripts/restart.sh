#!/bin/bash
# 重启 K1 后端（优先走 systemd；没有服务时退回 nohup）
export ZHIKONG_HOME=/opt/zhikong
mkdir -p /opt/zhikong/logs 2>/dev/null || true
mkdir -p /run/zhikong 2>/dev/null || echo 123456 | sudo -S -p '' mkdir -p /run/zhikong

wait_ready() {
  for i in $(seq 1 40); do
    if curl -s -m 1 http://127.0.0.1:8080/api/health > /dev/null 2>&1; then
      echo "ready after ${i}s"; return 0
    fi
    sleep 1
  done
  echo "NOT READY"
  return 1
}

if systemctl list-unit-files 2>/dev/null | grep -q zhikong-backend.service; then
  echo "restart via systemd"
  echo 123456 | sudo -S -p '' systemctl restart zhikong-backend
  wait_ready
  systemctl is-active zhikong-backend
else
  pid=$(ss -ltnp 2>/dev/null | awk '/:8080 /{print $NF}' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
  [ -n "$pid" ] && { echo "stopping backend pid=$pid"; kill "$pid" 2>/dev/null; sleep 1.2; }
  cd /opt/zhikong/app || exit 1
  nohup python3 -u -m backend.main > /opt/zhikong/logs/backend.out 2>&1 &
  echo $! > /opt/zhikong/logs/backend.pid
  echo "started pid=$(cat /opt/zhikong/logs/backend.pid)"
  wait_ready
fi

echo "--- health ---"
curl -s -m 5 http://127.0.0.1:8080/api/health
echo
echo "--- log tail ---"
tail -8 /opt/zhikong/logs/backend.out
