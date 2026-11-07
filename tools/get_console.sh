#!/bin/bash
pkill -9 -f chromium 2>/dev/null
sleep 3
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
rm -rf /tmp/clog
setsid nohup chromium-browser --ozone-platform=wayland --kiosk \
  --force-device-scale-factor=1 --enable-logging=stderr --v=1 \
  --user-data-dir=/tmp/clog --no-first-run --test-type --disable-gpu \
  --password-store=basic --app=http://127.0.0.1:8080/ \
  > /tmp/clog.log 2>&1 < /dev/null &
sleep 15
echo "=== 控制台错误 ==="
grep -aoE 'Uncaught[^"]{0,160}|SyntaxError[^"]{0,120}|ReferenceError[^"]{0,120}|TypeError[^"]{0,120}' /tmp/clog.log | head -8
echo
echo "=== CONSOLE 行 ==="
grep -a 'CONSOLE' /tmp/clog.log | tail -8
