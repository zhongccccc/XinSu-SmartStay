#!/bin/bash
PB=123456
echo "=== 服务身份 ==="
systemctl show zhikong-backend -p User -p ExecStart -p Environment 2>/dev/null

echo
echo "=== 当前后端进程属主 ==="
ps -o user,pid,cmd -p $(pgrep -f 'backend.main' | head -1) 2>/dev/null

echo
echo "=== 以 root 身份能连上 PipeWire 吗 ==="
echo "$PB" | sudo -S -p '' bash -c 'echo "  XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"; ls /run/user/1000/pipewire-0 2>/dev/null || echo "  (socket 存在但不属于 root)"'

echo
echo "=== 用 shiqi 身份播放（应能听到）==="
echo "$PB" | sudo -S -p '' -u shiqi bash -c 'XDG_RUNTIME_DIR=/run/user/1000 pw-play /opt/zhikong/app/assets/voice/8752f50dc4ce.wav; echo "  返回码=$?"'

echo
echo "=== 音频 wav 是什么内容（时长/采样率）==="
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=sample_rate,channels -of default=noprint_wrappers=1 /opt/zhikong/app/assets/voice/8752f50dc4ce.wav 2>/dev/null | head -8
