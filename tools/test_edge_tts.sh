#!/bin/bash
cd /tmp || exit 1
echo "=== edge-tts 生成一句 ==="
timeout 25 edge-tts --voice zh-CN-XiaoxiaoNeural \
  --text "您好，请把身份证放在读卡区" --write-media /tmp/e.mp3 2>&1 | head -5
ls -lh /tmp/e.mp3 2>/dev/null

if [ -s /tmp/e.mp3 ]; then
  ffmpeg -loglevel error -y -i /tmp/e.mp3 -ar 48000 -ac 1 /tmp/e.wav
  echo "  已转 wav: $(stat -c%s /tmp/e.wav 2>/dev/null) bytes"
  echo "=== 播放（请注意听）==="
  XDG_RUNTIME_DIR=/run/user/1000 pw-play /tmp/e.wav
  echo "  返回码=$?"
else
  echo "  edge-tts 没生成文件（网络可能被拦）"
fi
