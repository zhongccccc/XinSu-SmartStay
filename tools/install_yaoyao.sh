#!/bin/bash
PB=123456
SRC=/tmp/voice_y
DEST=/opt/zhikong/app/assets/voice

echo "=== 转 48k 单声道并安装（Yaoyao 女声）==="
n=0
for f in "$SRC"/*.wav; do
  b=$(basename "$f")
  out="$SRC/48_$b"
  ffmpeg -loglevel error -y -i "$f" -ar 48000 -ac 1 "$out" || continue
  echo "$PB" | sudo -S -p '' cp -f "$out" "$DEST/$b"
  n=$((n+1))
done
echo "  安装 $n 个"

echo
echo "=== 重启后端 ==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -o /dev/null -w '  HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

echo
echo "=== 播欢迎语（Yaoyao）==="
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 7
echo "  已播放"
