#!/bin/bash
PB=123456
ROOT=/opt/zhikong/idreader/rootfs
APP=/opt/zhikong/idreader

echo "$PB" | sudo -S -p '' mkdir -p $ROOT/lib
echo "$PB" | sudo -S -p '' ln -sf /usr/lib/aarch64-linux-gnu/ld-linux-aarch64.so.1 $ROOT/lib/ld-linux-aarch64.so.1
echo "$PB" | sudo -S -p '' ln -sfn /usr/lib $ROOT/lib64 2>/dev/null
ls -l $ROOT/lib/ld-linux-aarch64.so.1
echo "--- 再试 ---"
cd $APP
timeout 8 bash -c "echo $PB | sudo -S -p '' qemu-aarch64-static -L $ROOT $APP/bin/id_reader -a -p $APP/cfg/" 2>&1 | head -30
echo "--- done ---"
