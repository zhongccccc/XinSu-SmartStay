#!/bin/bash
PB=123456
F=/opt/zhikong/app/scripts/kiosk_session.sh
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
if "--window-position=0,0" not in s:
    s = s.replace("    --kiosk \\\n",
                  "    --kiosk \\\n    --window-position=0,0 --window-size=800,480 \\\n", 1)
    open(p, "w").write(s)
    print("已加窗口位置")
else:
    print("已存在")
PY
grep -n 'window-position' $F

pkill -9 -f chromium 2>/dev/null
sleep 2
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 35
echo "实例: $(pgrep -c -f 'chromium.*8080')"
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
grim /tmp/fix_view.png && echo "shot ok"
