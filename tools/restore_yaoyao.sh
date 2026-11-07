#!/bin/bash
PB=123456
DEST=/opt/zhikong/app/assets/voice
n=0
printf '=== 恢复 Yaoyao（前几版的 SAPI 女声）===\n'
for f in /tmp/voice_y/48_*.wav; do
  [ -e "$f" ] || continue
  b=$(basename "$f" | sed 's/^48_//')
  echo "$PB" | sudo -S -p '' cp -f "$f" "$DEST/$b"
  n=$((n+1))
done
printf 'restored: %s\n' "$n"

echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 18
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8080/api/health

curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 6
printf 'played\n'
