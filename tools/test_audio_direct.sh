#!/bin/bash
cd /opt/zhikong/app || exit 1
echo "=== 直接调 Audio.say 播一句 ==="
timeout 30 python3 - <<'PY'
import sys, time
sys.path.insert(0, '/opt/zhikong/app')
from backend.devices.audio import Audio, CARD
print('  声卡:', CARD)
a = Audio(log=lambda m: print('   ', m))
print('  espeak:', a.espeak, ' aplay:', a.aplay)
p = a.synth('欢迎光临，请将身份证放在读卡区')
print('  合成文件:', p)
if p:
    import subprocess
    r = subprocess.run(['aplay', '-D', CARD, '-q', p], capture_output=True, text=True)
    print('  aplay 返回码:', r.returncode, r.stderr[:200])
    print('  文件大小:', __import__('os').path.getsize(p))
PY
