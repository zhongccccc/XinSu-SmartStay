#!/bin/bash
echo "--- 播放工具 ---"
for c in pw-play paplay pw-cat wpctl pactl speaker-test; do
  p=$(command -v $c 2>/dev/null)
  if [ -n "$p" ]; then echo "  $c -> $p"; else echo "  $c 无"; fi
done

echo
echo "--- PipeWire 设备 ---"
wpctl status 2>/dev/null | sed -n '/Audio/,/Video/p' | head -20

echo
echo "--- 用 pw-play 试播 ---"
W=/tmp/tts_test.wav
[ -f "$W" ] || espeak-ng -v cmn -w "$W" "测试"
if command -v pw-play >/dev/null 2>&1; then
  pw-play "$W" 2>&1 | head -3 && echo "  pw-play 完成"
fi
