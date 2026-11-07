#!/bin/bash
PB=123456
for F in /opt/zhikong/app/scripts/kiosk_session.sh /opt/zhikong/app/scripts/app_launch.sh; do
  [ -f "$F" ] || continue
  if grep -q 'force-device-scale-factor' "$F"; then
    echo "$F: 已有"
  else
    python3 - "$F" <<'PY'
import sys, re
p = sys.argv[1]
s = open(p).read()
# 在 --disable-gpu 前插入缩放参数（两个脚本都有这个标志）
if '--disable-gpu' in s:
    s = s.replace('--disable-gpu', '--force-device-scale-factor=1 --disable-gpu', 1)
elif '--kiosk \\' in s:
    s = s.replace('--kiosk \\', '--kiosk \\\n    --force-device-scale-factor=1 \\', 1)
open(p, 'w').write(s)
print("已加缩放参数")
PY
  fi
  grep -c 'force-device-scale-factor' "$F" | sed "s|^|  $(basename $F): |"
done

pkill -9 -f chromium 2>/dev/null
sleep 3
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 40
echo "实例: $(pgrep -c -f 'chromium.*8080')"
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim /tmp/dpr.png && echo "shot ok"
