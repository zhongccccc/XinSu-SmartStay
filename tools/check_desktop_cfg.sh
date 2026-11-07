#!/bin/bash
echo "=== pcmanfm-qt 配置目录 ==="
ls -R ~/.config/pcmanfm-qt/ 2>/dev/null | head -20

echo
echo "=== settings.conf 关键项 ==="
for f in $(find ~/.config/pcmanfm-qt -name settings.conf 2>/dev/null); do
  echo "--- $f"
  grep -iE "single|click|open|Desktop" "$f" | head -12
done

echo
echo "=== lxqt 配置 ==="
ls ~/.config/lxqt/ 2>/dev/null
grep -riE "single|click" ~/.config/lxqt/*.conf 2>/dev/null | head -5

echo
echo "=== 会话里跑了哪些桌面组件 ==="
pgrep -af "pcmanfm|lxqt-panel|labwc" | cut -c1-70
