#!/bin/bash
PB=123456
LIBROOT=/opt/zhikong/idreader/rootfs/usr/lib/aarch64-linux-gnu
APP=/opt/zhikong/idreader

echo "=== 1. binfmt 是否已注册 aarch64 ==="
ls /proc/sys/fs/binfmt_misc/ 2>/dev/null | head -10
if [ -f /proc/sys/fs/binfmt_misc/qemu-aarch64 ]; then
  echo "已注册:"; head -5 /proc/sys/fs/binfmt_misc/qemu-aarch64
else
  echo "未注册，尝试加载"
fi

echo
echo "=== 2. 准备 arm64 解释器路径（宿主 /lib 下） ==="
echo "$PB" | sudo -S -p '' ln -sfn $LIBROOT/ld-linux-aarch64.so.1 /lib/ld-linux-aarch64.so.1
ls -l /lib/ld-linux-aarch64.so.1

echo
echo "=== 3. 直接执行（不经 -L）==="
echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
sleep 1
cd $APP
echo "$PB" | sudo -S -p '' env LD_LIBRARY_PATH=$LIBROOT:$APP/lib \
  timeout -s KILL 6 $APP/bin/id_reader -a -p $APP/cfg/ 2>&1 | head -15
echo "--- 退出码上方 ---"
