#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
sleep 1

cat > /tmp/fg.sh <<'EOF'
#!/bin/bash
exec /usr/bin/qemu-aarch64-static -L /opt/zhikong/idreader/rootfs \
  /opt/zhikong/idreader/bin/id_reader -p /opt/zhikong/idreader/cfg/
EOF
chmod +x /tmp/fg.sh

echo "=== 前台模式 8 秒 ==="
echo "$PB" | sudo -S -p '' timeout -s KILL 8 bash /tmp/fg.sh 2>&1 | head -40
echo "=== end ==="
