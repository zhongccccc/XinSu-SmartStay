#!/bin/bash
# 把一体机安装成桌面程序：应用菜单 + 桌面图标 + zhikong 命令
set -u
PB=123456
APP=/opt/zhikong/app

echo "=== 1. 权限与资源 ==="
echo "$PB" | sudo -S -p '' chmod +x $APP/scripts/app_launch.sh
echo "$PB" | sudo -S -p '' cp -f $APP/assets/zhikong.png /usr/share/pixmaps/zhikong.png 2>/dev/null

echo "=== 2. 应用菜单 ==="
echo "$PB" | sudo -S -p '' cp -f $APP/deploy/zhikong-app.desktop /usr/share/applications/zhikong-app.desktop
mkdir -p /home/shiqi/.local/share/applications
cp -f $APP/deploy/zhikong-app.desktop /home/shiqi/.local/share/applications/zhikong-app.desktop 2>/dev/null
echo "  /usr/share/applications/zhikong-app.desktop"

echo "=== 3. 桌面图标 ==="
DESK=/home/shiqi/Desktop
mkdir -p "$DESK"
cp -f $APP/deploy/zhikong-app.desktop "$DESK/芯宿智控.desktop"
chmod +x "$DESK/芯宿智控.desktop"
# 让文件管理器认为它是可信启动器（有 gvfs 时才生效）
gio set "$DESK/芯宿智控.desktop" metadata::trusted true 2>/dev/null || true
ls -l "$DESK/芯宿智控.desktop"

echo "=== 4. zhikong 命令 ==="
cat > /tmp/zhikong <<'EOF'
#!/bin/bash
# 芯宿·智控 运维命令
case "${1:-status}" in
  start)   /opt/zhikong/app/scripts/app_launch.sh ;;
  stop)    pkill -f "chromium.*127.0.0.1:8080"; echo "界面已关闭（后端仍在运行）" ;;
  restart) echo 123456 | sudo -S -p '' systemctl restart zhikong-backend; echo "后端已重启" ;;
  status)
    printf "%-22s %s\n" "后端服务" "$(systemctl is-active zhikong-backend)"
    printf "%-22s %s\n" "读卡服务" "$(systemctl is-active idreader)"
    printf "%-22s %s\n" "界面进程" "$(pgrep -c -f '[c]hromium.*8080')"
    curl -s -m 3 http://127.0.0.1:8080/api/health 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('%-22s %s' % ('摄像头', d['camera']['ok']))
    print('%-22s %s' % ('身份证服务', d['idcard']['online']))
    print('%-22s %s' % ('RFID', d['rfid']['online']))
except Exception:
    print('  后端未响应')
"
    ;;
  desktop) /opt/zhikong/app/scripts/mode_desktop.sh ;;
  kiosk)   /opt/zhikong/app/scripts/mode_kiosk.sh ;;
  *) echo "用法: zhikong [start|stop|restart|status|desktop|kiosk]" ;;
esac
EOF
echo "$PB" | sudo -S -p '' cp /tmp/zhikong /usr/local/bin/zhikong
echo "$PB" | sudo -S -p '' chmod +x /usr/local/bin/zhikong
rm -f /tmp/zhikong

echo "=== 5. 校验 .desktop 合法性 ==="
desktop-file-validate /usr/share/applications/zhikong-app.desktop 2>&1 || echo "  (desktop-file-validate 未安装，跳过)"

echo "=== 完成 ==="
ls -l /usr/share/applications/zhikong-app.desktop /usr/local/bin/zhikong
