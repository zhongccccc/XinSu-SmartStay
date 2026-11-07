#!/bin/bash
# 在 VNC 会话 :1 上启动 kiosk 并截图，用于远程验证界面
DISP="${1:-:1}"
export ZHIKONG_HOME=/opt/zhikong
export DISPLAY="$DISP"
export XAUTHORITY=/home/shiqi/.Xauthority

pkill -f "chromium.*127.0.0.1:8080" 2>/dev/null
sleep 1
nohup /opt/zhikong/app/scripts/start_kiosk.sh "$DISP" > /opt/zhikong/logs/kiosk.out 2>&1 &
echo "kiosk launching on $DISP"
for i in $(seq 1 20); do
  sleep 1
  if pgrep -f "chromium.*127.0.0.1:8080" > /dev/null; then echo "chromium up after ${i}s"; break; fi
done
sleep 6
mkdir -p /opt/zhikong/data/shots
import -window root /opt/zhikong/data/shots/shot_$(date +%H%M%S).png 2>/dev/null || \
  ffmpeg -loglevel error -y -f x11grab -video_size 1920x1080 -i "$DISP" -frames:v 1 /opt/zhikong/data/shots/shot.png
ls -lt /opt/zhikong/data/shots/ | head -3
echo "--- kiosk log ---"
tail -5 /opt/zhikong/logs/kiosk.out
