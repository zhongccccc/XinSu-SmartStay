#!/bin/bash
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
pkill -f 'user-data-dir=/tmp/chrome-co' 2>/dev/null
sleep 1
nohup chromium-browser --ozone-platform=x11 --disable-gpu \
  --user-data-dir=/tmp/chrome-co --no-first-run --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app='http://127.0.0.1:8080/?co=1' > /tmp/cco.log 2>&1 &
sleep 12
convert /tmp/co_root.png -crop 800x480+0+0 +repage /tmp/co_crop.png 2>/dev/null || true
import -window root /tmp/co_root.png && echo "root shot ok"
convert /tmp/co_root.png -crop 800x480+0+0 +repage /tmp/co_crop.png && echo "crop ok"
