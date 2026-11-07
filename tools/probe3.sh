#!/bin/bash
echo "===== DSI MODES ====="
cat /sys/class/drm/card1-DSI-1/modes 2>/dev/null | head -5
cat /sys/class/drm/card1-DSI-1/enabled
echo "===== CHROMIUM ====="
chromium-browser --version 2>&1 | head -2
echo "===== PIP LIST ====="
pip3 list 2>/dev/null | head -40
echo "===== TTS/ASR CANDIDATES ====="
for b in espeak espeak-ng pico2wave ekho festival flite mimic3 piper sherpa-onnx whisper vosk; do p=$(command -v $b 2>/dev/null); [ -n "$p" ] && echo "FOUND $b -> $p"; done
echo "===== VNC SCREENSHOT TEST ====="
which import scrot xwd ffmpeg 2>/dev/null
DISPLAY=:1 timeout 20 ffmpeg -loglevel error -f x11grab -video_size 1920x1080 -i :1 -frames:v 1 -y /tmp/shot.png 2>&1 | tail -3
ls -l /tmp/shot.png 2>/dev/null
echo "===== ALSA MIXER ====="
amixer -c 1 scontrols 2>&1 | head -20
echo "===== MEM/THERMAL ====="
cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null
echo "===== DONE3 ====="
