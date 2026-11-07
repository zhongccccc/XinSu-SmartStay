#!/bin/bash
echo "=== resample 48k + play ==="
W=$(ls /opt/zhikong/app/assets/voice/*.wav | head -1)
ffmpeg -loglevel error -y -i "$W" -ar 48000 -ac 1 /tmp/t48.wav && ls -l /tmp/t48.wav
aplay -q -D plughw:1,0 /tmp/t48.wav; echo "aplay48 exit=$?"
echo "=== amixer playback ==="
amixer -c 1 sget 'DAC' 2>&1 | head -5
amixer -c 1 sget 'Playback Polarity' 2>&1 | head -3
echo "=== wayland tools ==="
for b in grim wayshot wtype wlr-randr wlopm; do printf "%s: %s\n" $b "$(command -v $b)"; done
echo "=== screen output info ==="
export XDG_RUNTIME_DIR=/run/user/1000
echo "=== hw params of card ==="
cat /proc/asound/card1/pcm0p/sub0/hw_params 2>/dev/null || echo "no stream"
