#!/bin/bash
echo "=== kiosk 进程 ==="
pgrep -a -f 'chromium.*8080' | head -3 || echo "  chromium 未运行"
echo
echo "=== 显示会话 ==="
pgrep -a -f 'labwc|Xorg|wayvnc|x11vnc|vnc' | head -8
echo
echo "=== 已监听的 VNC 端口 ==="
ss -lntp 2>/dev/null | grep -E ':59[0-9][0-9]' || echo "  无 59xx 端口"
echo
echo "=== 用户会话 ==="
ps -u shiqi -o pid,cmd --sort=pid 2>/dev/null | head -15
echo
echo "=== 启动脚本 ==="
ls -l /opt/zhikong/app/scripts/app_launch.sh 2>/dev/null
