#!/bin/bash
set -u
PB=123456
ROOT=/opt/zhikong/idreader/rootfs
AO="-o Dir::Etc::sourcelist=/tmp/arm64.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/arm64lists -o APT::Architecture=arm64 -o APT::Get::List-Cleanup=0"
cd /tmp/arm64debs || exit 1

PKGS="libcap2:arm64 libacl1:arm64 libselinux1:arm64 libpcre2-8-0:arm64 libsystemd0:arm64 liblzma5:arm64 libzstd1:arm64 libcrypt1:arm64 libtinfo6:arm64 libncursesw6:arm64"
apt-get $AO download $PKGS 2>&1 | tail -4

for d in /tmp/arm64debs/*.deb; do
  [ -e "$d" ] || continue
  echo "$PB" | sudo -S -p '' dpkg-deb -x "$d" "$ROOT" 2>/dev/null
done
echo "libs now: $(ls $ROOT/usr/lib/aarch64-linux-gnu | wc -l)"

echo "--- run ---"
echo "$PB" | sudo -S -p '' timeout 10 bash /opt/zhikong/idreader/start.sh 2>&1 | head -20
