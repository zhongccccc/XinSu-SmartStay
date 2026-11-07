#!/bin/bash
PB=123456
cat > /tmp/idreader.service <<'EOF'
[Unit]
Description=ID card reader service (vendor aarch64 build via binfmt)
After=network.target

[Service]
Type=forking
PIDFile=/var/run/id_reader.pid
Environment=LD_LIBRARY_PATH=/opt/zhikong/idreader/rootfs/usr/lib/aarch64-linux-gnu:/opt/zhikong/idreader/lib
ExecStart=/opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
echo "$PB" | sudo -S -p '' cp /tmp/idreader.service /etc/systemd/system/idreader.service
echo "$PB" | sudo -S -p '' rm -f /var/run/id_reader.pid
echo "$PB" | sudo -S -p '' systemctl daemon-reload
echo "$PB" | sudo -S -p '' systemctl restart idreader.service
sleep 8
echo "=== 状态 ==="
systemctl is-active idreader.service
systemctl status idreader.service --no-pager 2>&1 | sed -n '3,8p'
echo "=== 7846 ==="
ss -ltnp 2>/dev/null | grep 7846 || echo "未监听"
echo "=== 读卡 ==="
curl -s -m 8 "http://127.0.0.1:7846/api/readCard?utf8=1"
echo
