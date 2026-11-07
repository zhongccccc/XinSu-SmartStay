#!/bin/bash
PB=123456
ROOT=/opt/zhikong/idreader/rootfs
APP=/opt/zhikong/idreader

echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
sleep 1

# 把宿主 /dev /sys /proc 链进 rootfs，解决 qemu -L 前缀把系统路径也前缀掉的问题
for d in dev sys proc run tmp; do
  echo "$PB" | sudo -S -p '' ln -sfn /$d $ROOT/$d
done
echo "$PB" | sudo -S -p '' mkdir -p $ROOT/etc
echo "$PB" | sudo -S -p '' cp -f /etc/nsswitch.conf $ROOT/etc/ 2>/dev/null
ls -l $ROOT | head -12

echo "--- 启动 ---"
cd $APP
echo "$PB" | sudo -S -p '' bash -c "setsid /opt/zhikong/idreader/start.sh > /opt/zhikong/idreader/service.out 2>&1 < /dev/null &"
sleep 6
echo "--- 端口 ---"
ss -ltnp 2>/dev/null | grep -E "7846|6045" || echo "no listen"
echo "--- 读卡 ---"
curl -s -m 8 "http://127.0.0.1:7846/api/readCard?utf8=1" | head -c 400
echo
echo "--- 服务输出 ---"
tail -8 /opt/zhikong/idreader/service.out 2>/dev/null
