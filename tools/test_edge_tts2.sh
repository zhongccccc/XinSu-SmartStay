#!/bin/bash
cd /tmp || exit 1
echo "=== 用模块方式调用 edge-tts ==="
timeout 30 python3 -m edge_tts --voice zh-CN-XiaoxiaoNeural \
  --text "您好，请把身份证放在读卡区" --write-media /tmp/e.mp3 2>&1 | tail -5
ls -l /tmp/e.mp3 2>/dev/null || echo "  没有生成文件"

if [ -s /tmp/e.mp3 ]; then
  ffmpeg -loglevel error -y -i /tmp/e.mp3 -ar 48000 -ac 1 /tmp/e.wav
  echo "  wav: $(stat -c%s /tmp/e.wav) bytes"
  XDG_RUNTIME_DIR=/run/user/1000 pw-play /tmp/e.wav
  echo "  播放返回码=$?"
fi
