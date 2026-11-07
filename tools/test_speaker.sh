#!/bin/bash
TXT="欢迎光临，请将身份证放在读卡区"
W=/tmp/tts_test.wav

echo "=== 合成 ==="
espeak-ng -v cmn -s 150 -p 55 -w /tmp/tts_raw.wav "$TXT" 2>&1 | head -3
ffmpeg -loglevel error -y -i /tmp/tts_raw.wav -ar 48000 -ac 1 "$W" && echo "  已生成 $W"
ls -lh "$W" | tail -1

echo
echo "=== 音量（card 0 / card 1）==="
amixer -c 0 sget PCM 2>/dev/null | tail -2
amixer -c 0 sset PCM 90% unmute 2>/dev/null | tail -1
amixer -c 1 sget 'Playback' 2>/dev/null | tail -2

echo
echo "=== 播到 card 0（USB 音箱）==="
aplay -D plughw:0,0 "$W" 2>&1 | head -3 && echo "  card0 播放完成"

sleep 1
echo
echo "=== 播到 card 1（板载）==="
aplay -D plughw:1,0 "$W" 2>&1 | head -3 && echo "  card1 播放完成"
