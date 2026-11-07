#!/bin/bash
PB=123456
V=/opt/zhikong/app/assets/voice
TMP=/tmp/voice_raw
mkdir -p "$TMP"

echo "=== 备份并处理 13 句（提亮+压缩，播音感）==="
for f in "$V"/*.wav; do
  b=$(basename "$f")
  # 只处理这次新装的 13 个（按大小特征跳过太小的）
  [ $(stat -c%s "$f") -lt 150000 ] && continue
  cp -f "$f" "$TMP/$b" 2>/dev/null
done
ls "$TMP" | wc -l | sed 's/^/  待处理: /'

echo
echo "=== 试处理第一句看效果 ==="
FIRST=$(ls -S "$TMP"/*.wav 2>/dev/null | head -1)
echo "  样本: $FIRST"
ffmpeg -loglevel error -y -i "$FIRST" \
  -af "highpass=f=90,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=8:release=120,alimiter=limit=0.95" \
  -ar 48000 -ac 1 /tmp/voice_test.wav && echo "  处理成功"
ls -l /tmp/voice_test.wav | awk '{print "  输出大小:", $5}'

echo
echo "=== 播放处理前后对比 ==="
echo "  1) 原始："
XDG_RUNTIME_DIR=/run/user/1000 pw-play "$FIRST" 2>/dev/null
sleep 1
echo "  2) 处理后："
XDG_RUNTIME_DIR=/run/user/1000 pw-play /tmp/voice_test.wav 2>/dev/null
echo "  播放完成"
