#!/bin/bash
PB=123456
DEST=/opt/zhikong/app/assets/voice
n=0
for f in /tmp/voice_new/*.wav; do
  [ -e "$f" ] || continue
  b=$(basename "$f")
  ffmpeg -loglevel error -y -i "$f" -ar 48000 -ac 1 "/tmp/vn_$b" || continue
  echo "$PB" | sudo -S -p '' cp -f "/tmp/vn_$b" "$DEST/$b"
  n=$((n+1))
done
printf 'installed new: %s\n' "$n"

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 18
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

printf '=== 试播退房引导 ===\n'
curl -s -X POST http://127.0.0.1:8080/api/checkout/guide > /dev/null
sleep 5
printf 'done\n'
