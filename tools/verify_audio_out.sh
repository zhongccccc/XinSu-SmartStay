#!/bin/bash
echo "=== 播放器与缓存 ==="
python3 - <<'PY'
import sys, os
sys.path.insert(0, '/opt/zhikong/app')
from backend.devices.audio import Audio, CARD
a = Audio(log=lambda m: print('  ', m))
print('  声卡:', CARD, ' 播放器:', 'pw-play' if a.pwplay else 'aplay')
print('  TTS:', bool(a.espeak))
p = a.synth('欢迎入住芯宿智控智慧酒店，请将身份证放在读卡区')
print('  音频文件:', p, os.path.getsize(p) if p else 0, 'bytes')
PY

echo
echo "=== 直接 pw-play 播一遍（请听小音箱）==="
W=$(ls -t /opt/zhikong/app/assets/voice/*.wav 2>/dev/null | head -1)
echo "  播放: $W"
pw-play "$W" 2>&1 | head -3
echo "  返回码: $?"
