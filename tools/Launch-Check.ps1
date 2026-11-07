$hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe'
$apps = @(
    @{ P = 'D:\XTS\code\SystemFeature\Notification\Publish'; B = 'com.samples.notificationpublish'; A = 'EntryAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch'; B = 'ohos.example.themeswitch'; A = 'MainAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\GamePuzzle'; B = 'ohos.samples.gamepuzzle'; A = 'MainAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\WindowManagement\WindowManage'; B = 'ohos.samples.windowcomponent'; A = 'MainAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\Security\CertificateFramework'; B = 'com.samples.certframework'; A = 'EntryAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\VoiceCallDemo'; B = 'com.samples.voicecalldemo'; A = 'EntryAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\Recorder'; B = 'ohos.samples.recorder'; A = 'EntryAbility' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\MusicPlayer'; B = 'com.samples.musicplayer'; A = 'EntryAbility' }
)

foreach ($a in $apps) {
    $name = Split-Path $a.P -Leaf
    $hap = Get-ChildItem (Join-Path $a.P 'entry\build\default\outputs\default') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $hap) { Write-Output ("{0,-26} NO HAP" -f $name); continue }
    & $hdc install -r $hap.FullName 2>&1 | Out-Null
    $start = & $hdc shell aa start -b $a.B -a $a.A 2>&1 | Out-String
    $ok = $start -match 'start ability successfully'
    Write-Output ("{0,-26} install+start={1}" -f $name, $(if ($ok) { 'OK' } else { 'FAIL: ' + ($start -replace "`r?`n", ' ') }))
    & $hdc shell aa force-stop $a.B 2>&1 | Out-Null
}
