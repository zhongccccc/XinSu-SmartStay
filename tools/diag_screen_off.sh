#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

echo "=== 系统 ==="
uptime
echo "=== 输出状态 ==="
wlr-randr 2>/dev/null | grep -E 'Enabled|Scale|800x480' | head -6
echo
echo "=== 相关进程 ==="
pgrep -a 'swayidle|wlopm|labwc' 2>/dev/null | head -5
echo "chromium: $(pgrep -c -f 'chromium.*8080')"
echo
echo "=== 休眠/熄屏相关日志 ==="
journalctl -b --no-pager 2>/dev/null | grep -iE 'dpms|blank|dim|dpms|backlight' | tail -6
echo
echo "=== 当前运行的应用 ==="
pgrep -a labwc | head -2
