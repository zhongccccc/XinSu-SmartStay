#!/bin/bash
# 预生成离线语音包（espeak-ng 中文 → 48kHz 单声道，匹配 ES8326 声卡）
set -u
OUT=/opt/zhikong/app/assets/voice
TMP=/tmp/zk_voice_tmp
mkdir -p "$OUT" "$TMP"
gen() {
  local text="$1"
  local hash
  hash=$(printf '%s' "$text" | md5sum | cut -c1-12)
  if [ ! -s "$OUT/$hash.wav" ]; then
    espeak-ng -v cmn -s 150 -p 55 -w "$TMP/raw.wav" "$text" 2>/dev/null || return
    ffmpeg -loglevel error -y -i "$TMP/raw.wav" -ar 48000 -ac 1 "$OUT/$hash.wav" 2>/dev/null
    echo "gen $hash  $text"
  fi
}

gen "欢迎入住芯宿智控智慧酒店，请将身份证放在读卡区"
gen "身份核验通过，请正对摄像头，为您采集人脸"
gen "人脸比对成功，请选择您喜欢的房间"
gen "已选择房间，请扫描付款码支付"
gen "支付成功，请将房卡放在读卡区为您写卡"
gen "房卡写入成功，正在为您下发门锁权限"
gen "开锁凭证已下发，祝您入住愉快"
gen "欢迎光临，请触摸屏幕开始入住"
gen "已取消，欢迎再次使用"
gen "芯宿智控自助入住一体机已启动"
gen "已为您呼叫服务，请稍候"

rm -f "$OUT"/*.wav.raw "$TMP/raw.wav"
echo "voice pack ready: $(ls -1 "$OUT"/*.wav 2>/dev/null | wc -l) files"
