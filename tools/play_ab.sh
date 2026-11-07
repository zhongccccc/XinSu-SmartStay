#!/bin/bash
cd /tmp/aud || exit 1
for f in A_piper.wav B_fanchen.wav; do
  [ -e "$f" ] || continue
  ffmpeg -loglevel error -y -i "$f" -ar 48000 -ac 1 "p_$f"
done
printf 'A: Piper huayan\n'
XDG_RUNTIME_DIR=/run/user/1000 pw-play p_A_piper.wav
sleep 2
printf 'B: fanchen\n'
XDG_RUNTIME_DIR=/run/user/1000 pw-play p_B_fanchen.wav
printf 'done\n'
