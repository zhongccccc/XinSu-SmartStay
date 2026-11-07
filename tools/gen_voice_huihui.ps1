# 用 Windows 中文语音（Huihui）预生成播报音频
# 文件名 = md5(utf8 文本)[:12].wav，与后端 Audio.wav_path 完全一致
Add-Type -AssemblyName System.Speech

$out = 'E:\zhikong\tmp_voice'
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Path $out | Out-Null }

$sentences = @(
  '欢迎入住芯宿智控智慧酒店，请将身份证放在读卡区',
  '身份核验通过，请正对摄像头，为您采集人脸',
  '人脸比对成功，请选择您喜欢的房间',
  '人脸比对未通过，请正对摄像头再试一次',
  '已选择房间，请扫描付款码支付',
  '支付成功，请将房卡放在读卡区为您写卡',
  '房卡写入成功，正在为您下发门锁权限',
  '办理完成，请取走身份证和房卡，到房间输入开门码即可开锁',
  '退房成功，开门凭证已作废',
  '门锁未响应，开门码已生成，请到前台处理',
  '开门码已生成，祝您入住愉快',
  '已取消，欢迎再次使用',
  '已返回待机'
)

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Huihui Desktop')
$synth.Rate = -1
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(
  48000,
  [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,
  [System.Speech.AudioFormat.AudioChannel]::Mono
)

$md5 = [System.Security.Cryptography.MD5]::Create()
foreach ($t in $sentences) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($t)
  $hash = -join ($md5.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
  $name = $hash.Substring(0, 12)
  $path = Join-Path $out "$name.wav"
  $synth.SetOutputToWaveFile($path, $fmt)
  $synth.Speak($t)
  $synth.SetOutputToNull()
  $size = (Get-Item $path).Length
  "{0,-14} {1,8:N0} B  {2}" -f $name, $size, $t
}
$synth.Dispose()
"---"
"共生成 " + (Get-ChildItem $out -Filter *.wav).Count + " 个文件 -> $out"
