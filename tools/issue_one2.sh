#!/bin/bash
PB=123456
B=http://127.0.0.1:8080

ROOM=$(cat /tmp/one_room.txt 2>/dev/null)
CODE=$(cat /tmp/one_code.txt 2>/dev/null)
[ -z "$ROOM" ] && ROOM=8808 && CODE=135790
echo "测试目标: 房间 $ROOM  开门码 $CODE"

echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend
sleep 3
echo "$PB" | sudo -S -p '' python3 /opt/zhikong/tools/zk_send2.py \
  "zk revoke" \
  "zk issue $ROOM $CODE - 1440" \
  "zk code $CODE" 2>&1 | head -18
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "后端: $(systemctl is-active zhikong-backend)"
