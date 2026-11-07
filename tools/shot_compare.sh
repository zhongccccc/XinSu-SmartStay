#!/bin/bash
# 分别截取：客人视角(服务面板) / 前台视角(服务面板)
export DISPLAY=:1
export XAUTHORITY=/home/shiqi/.Xauthority

shot() {
  local url="$1"
  local out="$2"
  pkill -f 'user-data-dir=/tmp/chrome-cmp' 2>/dev/null
  sleep 1
  rm -rf /tmp/chrome-cmp
  nohup chromium-browser --ozone-platform=x11 --disable-gpu \
    --user-data-dir=/tmp/chrome-cmp --no-first-run --test-type --password-store=basic \
    --window-size=800,480 --window-position=0,0 \
    --app="$url" > /tmp/cmp.log 2>&1 &
  sleep 12
  import -window root /tmp/cmp_root.png
  convert /tmp/cmp_root.png -crop 800x480+0+0 +repage "$out"
  echo "  $out"
}

shot 'http://127.0.0.1:8080/?svc=1' /tmp/view_guest.png
shot 'http://127.0.0.1:8080/?svc=1&staff=1' /tmp/view_staff.png
