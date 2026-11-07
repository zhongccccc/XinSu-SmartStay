#!/bin/bash
PB=123456
ROOT=/opt/zhikong/idreader/rootfs
LIBDIR=$ROOT/usr/lib/aarch64-linux-gnu
APP=/opt/zhikong/idreader

echo "$PB" | sudo -S -p '' cp -f $APP/lib/libsdtapi.so $APP/lib/libbland.so $APP/lib/libidreader.so $LIBDIR/
echo "$PB" | sudo -S -p '' chmod 755 $APP/bin/id_reader
echo "--- 试运行（前台 6 秒）---"
cd $APP
timeout 6 bash -c "echo $PB | sudo -S -p '' qemu-aarch64-static -L $ROOT $APP/bin/id_reader -a -p $APP/cfg/" 2>&1 | head -30
echo "--- exit=$? ---"
