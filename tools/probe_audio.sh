#!/bin/bash
echo "=== 声卡 ==="
aplay -l 2>/dev/null | head -12
echo "默认输出:"
pactl info 2>/dev/null | grep -E 'Default Sink|Server Name' || echo "  (无 pulseaudio)"

echo
echo "=== TTS 工具 ==="
for c in espeak-ng espeak ekho festival pico2wave mimic3 spd-say; do
  p=$(command -v $c 2>/dev/null)
  if [ -n "$p" ]; then echo "  $c -> $p"; else echo "  $c 无"; fi
done

echo
echo "=== espeak-ng 中文支持 ==="
if command -v espeak-ng >/dev/null 2>&1; then
  espeak-ng --voices 2>/dev/null | grep -i -E 'zh|chinese|mandarin' | head -5
else
  echo "  未安装 espeak-ng"
fi

echo
echo "=== 播放器 ==="
for c in aplay paplay ffplay mpv; do
  p=$(command -v $c 2>/dev/null)
  [ -n "$p" ] && echo "  $c -> $p"
done

echo
echo "=== 后端现有的 say 实现 ==="
grep -rn "def _say" /opt/zhikong/app/backend/core/model.py | head -3
grep -rn "class .*Audio\|def say" /opt/zhikong/app/backend/devices/*.py | head -8
