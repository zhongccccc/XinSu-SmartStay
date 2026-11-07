#!/bin/bash
V=/opt/zhikong/app/assets/voice
printf '=== 新音频 ===\n'
for h in 2a493c9d5dcc 64371c0b893a 83af39ad18b5; do
  if [ -f "$V/$h.wav" ]; then
    printf '  %s  %s bytes\n' "$h" "$(stat -c%s "$V/$h.wav")"
  else
    printf '  %s  缺失\n' "$h"
  fi
done

printf '\n=== 退房引导接口 ===\n'
curl -s -X POST http://127.0.0.1:8080/api/checkout/guide | head -c 100
printf '\n'

printf '\n=== 重启界面 ===\n'
bash /opt/zhikong/tools/start_both.sh > /dev/null 2>&1
sleep 14
printf '  chromium: %s\n' "$(pgrep -c -f 'chromium.*8080')"
