#!/bin/bash
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority
pkill -f 'user-data-dir=/tmp/chrome-adm' 2>/dev/null
sleep 1
rm -rf /tmp/chrome-adm
nohup chromium-browser --ozone-platform=x11 --disable-gpu \
  --user-data-dir=/tmp/chrome-adm --no-first-run --test-type --password-store=basic \
  --window-size=800,480 --window-position=0,0 \
  --app='http://127.0.0.1:8080/?admin=1' > /tmp/cadm.log 2>&1 &
sleep 14
import -window root /tmp/adm_ip.png && echo "shot ok"
convert /tmp/adm_ip.png -crop 800x480+0+0 +repage /tmp/adm_ip_crop.png
