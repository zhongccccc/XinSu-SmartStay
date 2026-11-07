#!/bin/bash
echo "=== wayland sessions ==="
ls /usr/share/wayland-sessions/ 2>/dev/null
echo "=== xsessions ==="
ls /usr/share/xsessions/ 2>/dev/null
echo "=== session desktop files ==="
for f in /usr/share/wayland-sessions/*.desktop /usr/share/xsessions/*.desktop; do
  [ -f "$f" ] && { echo "--- $f"; grep -E '^(Name|Exec|DesktopNames)=' "$f"; }
done
echo "=== sddm conf ==="
ls /etc/sddm.conf.d/ 2>/dev/null; cat /etc/sddm.conf.d/*.conf 2>/dev/null | head -30
echo "=== autostart dir ==="
ls -la /home/shiqi/.config/autostart/ 2>/dev/null
cat /home/shiqi/.config/labwc/autostart 2>/dev/null
echo "=== current seat ==="
loginctl list-sessions 2>/dev/null
loginctl show-seat seat0 -p ActiveSession 2>/dev/null
echo "=== audio test ==="
W=$(ls /opt/zhikong/app/assets/voice/*.wav | head -1)
aplay -q -D plughw:1,0 "$W"; echo "aplay exit=$?"
