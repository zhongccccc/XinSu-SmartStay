#!/bin/bash
echo "=== 外网联通性 ==="
for u in https://pypi.org/simple/ https://www.baidu.com; do
  code=$(timeout 8 curl -s -o /dev/null -w '%{http_code}' "$u" 2>/dev/null)
  echo "  $u -> ${code:-超时}"
done

echo
echo "=== pip ==="
python3 -m pip --version 2>&1 | head -2

echo
echo "=== 现有 TTS 引擎 ==="
espeak-ng --version 2>/dev/null | head -1
echo "  中文音色数据:"
ls /usr/lib/*/espeak-ng-data/lang/sit/ 2>/dev/null | head -5
ls /usr/share/espeak-ng-data/lang/sit/ 2>/dev/null | head -5

echo
echo "=== 可选：edge-tts 是否已装 ==="
python3 -c "import edge_tts; print('  已安装', edge_tts.__version__)" 2>/dev/null || echo "  未安装"
