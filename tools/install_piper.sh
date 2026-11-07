#!/bin/bash
PB=123456
SRC=/tmp/voice_p
DEST=/opt/zhikong/app/assets/voice
mkdir -p /tmp/voice_p48

n=0
for f in "$SRC"/*.wav; do
  [ -e "$f" ] || continue
  b=$(basename "$f")
  ffmpeg -loglevel error -y -i "$f" -ar 48000 -ac 1 "/tmp/voice_p48/$b" || continue
  echo "$PB" | sudo -S -p '' cp -f "/tmp/voice_p48/$b" "$DEST/$b"
  n=$((n+1))
done
printf 'installed: %s\n' "$n"

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 7
printf 'played\n'
