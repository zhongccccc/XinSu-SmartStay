#!/bin/bash
for i in 1 2 3; do
  echo "--- try $i ---"
  curl -s -m 10 'http://127.0.0.1:7846/api/readCard?utf8=1'
  echo
  sleep 2
done
echo "--- 服务日志 ---"
journalctl -u idreader --no-pager -n 8 | tail -8
echo "--- 服务状态 ---"
systemctl is-active idreader
