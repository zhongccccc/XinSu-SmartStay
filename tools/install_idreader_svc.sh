#!/bin/bash
# 把厂商 aarch64 版读卡服务通过 binfmt 跑起来，并做成开机自启
set -u
PB=123456
APP=/opt/zhikong/idreader
LIBROOT=$APP/rootfs/usr/lib/aarch64-linux-gnu

echo "=== 1. 停掉临时进程 ==="
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
sleep 1

echo "=== 2. 解释器路径 + 库 ==="
echo "$PB" | sudo -S -p '' ln -sfn $LIBROOT/ld-linux-aarch64.so.1 /lib/ld-linux-aarch64.so.1
echo "$PB" | sudo -S -p '' cp -f $APP/lib/*.so $LIBROOT/ 2>/dev/null
cp -f $APP/lib/*.so $LIBROOT/ 2>/dev/null || true

echo "=== 3. 写 systemd 单元 ==="
cat > /tmp/idreader.service <<'EOF'
[Unit]
Description=ID card reader service (vendor aarch64 build via binfmt)
After=network.target

[Service]
Type=simple
Environment=LD_LIBRARY_PATH=/opt/zhikong/idreader/rootfs/usr/lib/aarch64-linux-gnu:/opt/zhikong/idreader/lib
ExecStart=/opt/zhikong/idreader/bin/id_reader -a -p /opt/zhikong/idreader/cfg/
Restart=always
RestartSec=3
User=root
StandardOutput=append:/opt/zhikong/logs/idreader.out
StandardError=append:/opt/zhikong/logs/idreader.out

[Install]
WantedBy=multi-user.target
EOF
echo "$PB" | sudo -S -p '' cp /tmp/idreader.service /etc/systemd/system/idreader.service
echo "$PB" | sudo -S -p '' systemctl daemon-reload
echo "$PB" | sudo -S -p '' systemctl enable idreader.service > /dev/null 2>&1
echo "$PB" | sudo -S -p '' systemctl restart idreader.service
sleep 6

echo "=== 4. 状态 ==="
systemctl is-active idreader.service
ss -ltnp 2>/dev/null | grep 7846 || echo "7846 未监听"
echo "=== 5. 读卡（有卡就返回证件）==="
curl -s -m 8 "http://127.0.0.1:7846/api/readCard?utf8=1"
echo
