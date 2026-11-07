#!/bin/bash
echo "=== all mixer controls ==="
amixer -c 1 scontrols | sed 's/Simple mixer control //'
echo "=== trigger tts ==="
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 6
echo "=== backend log ==="
tail -6 /opt/zhikong/logs/backend.out
echo "=== aplay manual 48k ==="
W=$(ls -S /opt/zhikong/app/assets/voice/*.wav | head -1)
timeout 30 aplay -D plughw:1,0 "$W" && echo "PLAY_OK"
