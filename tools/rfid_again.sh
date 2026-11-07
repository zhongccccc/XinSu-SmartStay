#!/bin/bash
echo "=== 上次抓包结果 ==="
if [ -f /tmp/rfid_cap.txt ]; then
  cat /tmp/rfid_cap.txt
else
  echo "(没有记录文件)"
fi
echo
echo "=== 重新开始监听（约 70 秒）==="
echo 123456 | sudo -S -p '' systemctl stop zhikong-backend
sleep 1
sudo -b python3 /tmp/rcap.py > /tmp/rcap.log 2>&1
echo "监听已启动"
