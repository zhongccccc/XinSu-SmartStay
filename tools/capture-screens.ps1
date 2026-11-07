param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe'
)

$apps = @(
    @{ P = 'D:\XTS\code\SystemFeature\Notification\Publish'; B = 'com.samples.notificationpublish'; A = 'EntryAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch'; B = 'ohos.example.themeswitch'; A = 'MainAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\GamePuzzle'; B = 'ohos.samples.gamepuzzle'; A = 'MainAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\WindowManagement\WindowManage'; B = 'ohos.samples.windowcomponent'; A = 'MainAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\Security\CertificateFramework'; B = 'com.samples.certframework'; A = 'EntryAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\VoiceCallDemo'; B = 'com.samples.voicecalldemo'; A = 'EntryAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\Recorder'; B = 'ohos.samples.recorder'; A = 'EntryAbility'; Img = 'device_main.jpeg' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\MusicPlayer'; B = 'com.samples.musicplayer'; A = 'EntryAbility'; Img = 'device_main.jpeg' }
)

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell "uinput -K -d 224 -u 224" 2>&1 | Out-Null
Start-Sleep -Seconds 2

foreach ($app in $apps) {
    $name = Split-Path $app.P -Leaf
    $hap = Get-ChildItem (Join-Path $app.P 'entry\build\default\outputs\default') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $hap) { Write-Output "$name : NO HAP"; continue }
    & $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
    & $Hdc install -r $hap.FullName 2>&1 | Out-Null
    & $Hdc shell aa force-stop $app.B 2>&1 | Out-Null
    & $Hdc shell aa start -b $app.B -a $app.A 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    # 处理可能出现的权限弹窗（允许按钮约在屏幕 71% 宽、57.5% 高）
    & $Hdc shell "uitest uiInput click 511 736" 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    $remote = "/data/local/tmp/$($app.Img)"
    & $Hdc shell "snapshot_display -f $remote" 2>&1 | Out-Null
    $outDir = Join-Path $app.P 'screenshots'
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    $local = Join-Path $outDir $app.Img
    if (Test-Path $local) { Remove-Item $local -Force }
    & $Hdc file recv $remote $local 2>&1 | Out-Null
    $size = 0
    if (Test-Path $local) { $size = (Get-Item $local).Length }
    Write-Output ("{0,-26} screenshot={1} size={2}" -f $name, $(if ($size -gt 1000) { 'OK' } else { 'FAIL' }), $size)
}
