#!/bin/bash
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
pkill -f 'user-data-dir=/tmp/chrome-co2' 2>/dev/null
sleep 1
rm -rf /tmp/chrome-co2
nohup chromium-browser --ozone-platform=x11 --disable-gpu \
  --user-data-dir=/tmp/chrome-co2 --no-first-run --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app='http://127.0.0.1:8080/?cocode=1' > /tmp/cco2.log 2>&1 &
sleep 13
import -window root /tmp/co2_root.png && echo "shot ok"
convert /tmp/co2_root.png -crop 800x480+0+0 +repage /tmp/co2_crop.png && echo "crop ok"
