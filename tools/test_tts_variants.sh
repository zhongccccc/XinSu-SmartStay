#!/bin/bash
PB=123456
TXT="您好，请把身份证放在读卡区"

echo "=== 以 root 身份、切换到 shiqi 播放（模拟后端环境）==="
for sp in 150 120 95; do
  espeak-ng -v cmn -s $sp -p 55 -w /tmp/v_$sp.wav "$TXT" 2>/dev/null
  echo "  语速 $sp：播放中…"
  echo "$PB" | sudo -S -p '' env XDG_RUNTIME_DIR=/run/user/1000 \
    setpriv --reuid=1000 --regid=1000 --init-groups \
    pw-play /tmp/v_$sp.wav 2>&1 | head -2
  echo "    返回码=$?"
  sleep 1
done

echo
echo "=== 重启后端并触发欢迎语 ==="
echo "$PB" | sudo -S -p '' systemctl restart zhikong-backend
sleep 20
curl -s -X POST http://127.0.0.1:8080/api/cancel > /dev/null
sleep 1
curl -s -X POST http://127.0.0.1:8080/api/session/start > /dev/null
sleep 8
echo "  已触发（应听到欢迎语）"
echo
echo "=== 后端 audio 日志 ==="
grep -a '\[audio\]' /opt/zhikong/logs/backend.log | tail -5
