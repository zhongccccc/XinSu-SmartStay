#!/bin/bash
PB=123456
# 单元里 PIDFile 用 /run，去掉 legacy 警告
sed -i 's#PIDFile=/var/run/id_reader.pid#PIDFile=/run/id_reader.pid#' /etc/systemd/system/idreader.service 2>/dev/null
echo "$PB" | sudo -S -p '' systemctl daemon-reload
bash /opt/zhikong/app/scripts/restart.sh 2>&1 | head -3
sleep 3
echo "=== 现在重启整机 ==="
echo "$PB" | sudo -S -p '' systemctl reboot
