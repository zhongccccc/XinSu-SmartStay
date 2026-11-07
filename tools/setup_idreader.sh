#!/bin/bash
# 为厂商 aarch64 版 id_reader 搭建 qemu 运行环境
set -u
PB=123456
export DEBIAN_FRONTEND=noninteractive

echo "=== 1. 安装 qemu-user-static ==="
echo "$PB" | sudo -S -p '' apt-get install -y qemu-user-static > /tmp/qemu_install.log 2>&1
echo "apt exit=$?"
tail -3 /tmp/qemu_install.log
command -v qemu-aarch64-static || exit 1

echo
echo "=== 2. 准备 arm64 软件源 ==="
cat > /tmp/arm64.list <<'EOF'
deb [arch=arm64] http://ports.ubuntu.com/ubuntu-ports noble main universe
deb [arch=arm64] http://ports.ubuntu.com/ubuntu-ports noble-updates main universe
EOF
mkdir -p /tmp/arm64lists /tmp/arm64debs
AO="-o Dir::Etc::sourcelist=/tmp/arm64.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/arm64lists -o APT::Architecture=arm64 -o APT::Get::List-Cleanup=0"
apt-get $AO update > /tmp/arm64_update.log 2>&1
echo "update exit=$?"
tail -2 /tmp/arm64_update.log

cd /tmp/arm64debs || exit 1
rm -f *.deb
apt-get $AO download libc6:arm64 libstdc++6:arm64 libgcc-s1:arm64 libudev1:arm64 libusb-1.0-0:arm64 2>&1 | tail -6
ls -1 *.deb 2>/dev/null | head

echo
echo "=== 3. 解包到 rootfs ==="
ROOT=/opt/zhikong/idreader/rootfs
echo "$PB" | sudo -S -p '' mkdir -p "$ROOT" /opt/zhikong/idreader/lib /opt/zhikong/idreader/bin /opt/zhikong/idreader/cfg
for d in /tmp/arm64debs/*.deb; do
  [ -e "$d" ] || continue
  echo "$PB" | sudo -S -p '' dpkg-deb -x "$d" "$ROOT"
done
echo "$PB" | sudo -S -p '' cp -f /tmp/bins/id_reader /opt/zhikong/idreader/bin/
echo "$PB" | sudo -S -p '' cp -f /tmp/bins/libsdtapi.so /tmp/bins/libbland.so /tmp/bins/libidreader.so /opt/zhikong/idreader/lib/
echo "$PB" | sudo -S -p '' chown -R shiqi:shiqi /opt/zhikong/idreader
ls -l /opt/zhikong/idreader/bin /opt/zhikong/idreader/lib
ls "$ROOT/usr/lib/aarch64-linux-gnu" 2>/dev/null | head -10
