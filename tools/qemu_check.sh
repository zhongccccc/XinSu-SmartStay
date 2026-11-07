#!/bin/bash
echo "=== 已有 qemu/box64? ==="
for b in qemu-aarch64-static qemu-aarch64 box64 box86 focker; do printf "%-20s %s\n" $b "$(command -v $b)"; done
echo "=== apt 源里有没有 qemu-user-static ==="
apt-cache policy qemu-user-static 2>/dev/null | head -5
echo "=== 当前架构 ==="
dpkg --print-architecture
echo "=== 外网通不通（ports.ubuntu.com）==="
timeout 8 curl -sI http://ports.ubuntu.com/ubuntu-ports/ 2>&1 | head -3
