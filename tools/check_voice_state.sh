#!/bin/bash
DEST=/opt/zhikong/app/assets/voice
printf '=== 目标文件时间与大小 ===\n'
ls -l "$DEST/e1f204969354.wav" "$DEST/7569cb8d37b9.wav" 2>/dev/null
printf '\n=== /tmp/voice_y 内容 ===\n'
ls -l /tmp/voice_y 2>/dev/null | head -5
printf '\n=== ffprobe 采样率 ===\n'
ffprobe -v error -show_entries stream=sample_rate,channels -of default=noprint_wrappers=1 "$DEST/e1f204969354.wav" 2>/dev/null
