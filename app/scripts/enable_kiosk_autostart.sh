#!/bin/bash
# 开机直接进一体机 kiosk（物理触摸屏 seat0 / labwc Wayland 会话）
set -e
PB='123456'

# 1) sddm 自动登录 shiqi，使用 labwc 会话（先写临时文件，避免 heredoc 抢 stdin）
cat > /tmp/99-zhikong-kiosk.conf <<'EOF'
[Autologin]
User=shiqi
Session=labwc
Relogin=true
EOF
echo "$PB" | sudo -S -p '' cp /tmp/99-zhikong-kiosk.conf /etc/sddm.conf.d/99-zhikong-kiosk.conf
echo "$PB" | sudo -S -p '' chmod 644 /etc/sddm.conf.d/99-zhikong-kiosk.conf

# 2) 打开自启开关
echo "$PB" | sudo -S -p '' mkdir -p /opt/zhikong/etc
echo "$PB" | sudo -S -p '' touch /opt/zhikong/etc/kiosk_autostart.enabled
echo "$PB" | sudo -S -p '' chown -R shiqi:shiqi /opt/zhikong/etc

# 3) 在 labwc autostart 顶部插入 kiosk 钩子
AS=/home/shiqi/.config/labwc/autostart
mkdir -p /home/shiqi/.config/labwc
touch "$AS"
if ! grep -q 'zhikong-kiosk-hook' "$AS" 2>/dev/null; then
  cp "$AS" "$AS.bak.zhikong" 2>/dev/null || true
  TMP=/tmp/zk_autostart.new
  cat > "$TMP" <<'EOF'
# --- zhikong-kiosk-hook ---
if [ -f /opt/zhikong/etc/kiosk_autostart.enabled ]; then
  /opt/zhikong/app/scripts/kiosk_session.sh > /opt/zhikong/logs/kiosk_seat0.log 2>&1 &
  { return 0; } 2>/dev/null || exit 0
fi
# --- /zhikong-kiosk-hook ---
EOF
  cat "$AS" >> "$TMP"
  mv "$TMP" "$AS"
  chmod +x "$AS"
fi

echo "config written; restarting sddm"
echo "$PB" | sudo -S -p '' systemctl restart sddm
sleep 10
echo "--- sessions ---"
loginctl list-sessions
echo "--- active seat ---"
loginctl show-seat seat0 -p ActiveSession 2>/dev/null
echo "--- wayland ---"
ls /run/user/1000/ | grep -i wayland || true
