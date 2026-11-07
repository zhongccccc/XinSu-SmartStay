#!/bin/bash
echo "=== 国内源连通性 ==="
for u in \
  https://pypi.tuna.tsinghua.edu.cn/simple/ \
  https://mirrors.aliyun.com/pypi/simple/ \
  https://mirrors.ustc.edu.cn/pypi/simple/ \
  https://www.modelscope.cn \
  https://hf-mirror.com \
  https://pypi.org/simple/ ; do
  code=$(timeout 8 curl -s -o /dev/null -w '%{http_code}' "$u" 2>/dev/null)
  printf '  %-45s %s\n' "$u" "${code:-超时}"
done

echo
echo "=== apt 里有没有中文 TTS 包 ==="
apt-cache policy ekho 2>/dev/null | head -4
apt-cache search --names-only 'tts|speech' 2>/dev/null | grep -iE 'ekho|piper|festival|espeak' | head -6

echo
echo "=== 已装的 python 包 ==="
python3 -m pip list 2>/dev/null | grep -iE 'piper|tts|onnx|pinyin' | head -8
