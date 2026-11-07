#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
PID=$(pgrep -f 'chromium.*8080' | head -1)
if [ -n "$PID" ]; then
  echo "=== chromium 进程 ==="
  ps -o pid,etime,cmd -p "$PID" | tail -1 | cut -c1-90
else
  echo "=== 没有界面进程 ==="
fi
grim /tmp/state_now.png && echo "shot ok"
