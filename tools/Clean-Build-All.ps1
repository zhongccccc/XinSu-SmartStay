param(
    [switch]$SkipTests
)

$pwshExe = (Get-Process -Id $PID).Path
$projects = @(
    @{ P = 'D:\XTS\code\SystemFeature\Notification\Publish'; B = 'com.samples.notificationpublish' },
    @{ P = 'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch'; B = 'ohos.example.themeswitch' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\GamePuzzle'; B = 'ohos.samples.gamepuzzle' },
    @{ P = 'D:\XTS\code\SystemFeature\WindowManagement\WindowManage'; B = 'ohos.samples.windowcomponent' },
    @{ P = 'D:\XTS\code\SystemFeature\Security\CertificateFramework'; B = 'com.samples.certframework' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\VoiceCallDemo'; B = 'com.samples.voicecalldemo' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\Recorder'; B = 'ohos.samples.recorder' },
    @{ P = 'D:\XTS\code\SystemFeature\Media\MusicPlayer'; B = 'com.samples.musicplayer' }
)

foreach ($t in $projects) {
    $name = Split-Path $t.P -Leaf
    # 清理构建缓存（保留 oh_modules 与签名材料）
    foreach ($dir in @('build', '.hvigor', 'entry\build', 'musicplayer\build')) {
        $target = Join-Path $t.P $dir
        if (Test-Path $target) { Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue }
    }
    $appOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Build-Project.ps1' -ProjectDir $t.P 2>&1
    $testOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Build-Project.ps1' -ProjectDir $t.P -TestTarget 2>&1
    $buildOk = (($appOut -join ' ') -match 'BUILD SUCCESSFUL') -and (($testOut -join ' ') -match 'BUILD SUCCESSFUL')
    $testResult = 'SKIP'
    if (-not $SkipTests) {
        $runOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Run-Tests.ps1' -ProjectDir $t.P -Bundle $t.B 2>&1
        $summary = ($runOut | Where-Object { $_ -match 'OHOS_REPORT_RESULT' }) -join ''
        $testResult = if ($summary) { $summary.Trim() } else { 'NO RESULT' }
    }
    Write-Output ("{0,-26} cleanBuild={1} {2}" -f $name, $(if ($buildOk) { 'OK' } else { 'FAIL' }), $testResult)
}
