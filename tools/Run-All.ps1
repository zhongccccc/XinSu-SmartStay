param(
    [switch]$SkipBuild
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

$results = @()
foreach ($t in $projects) {
    $name = Split-Path $t.P -Leaf
    $buildResult = 'SKIP'
    if (-not $SkipBuild) {
        $buildOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Build-Project.ps1' -ProjectDir $t.P 2>&1
        $testBuildOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Build-Project.ps1' -ProjectDir $t.P -TestTarget 2>&1
        $buildResult = if (($buildOut -join ' ') -match 'BUILD SUCCESSFUL' -and ($testBuildOut -join ' ') -match 'BUILD SUCCESSFUL') { 'OK' } else { 'FAIL' }
    }
    $testOut = & $pwshExe -NoProfile -ExecutionPolicy Bypass -File 'E:\zhikong\tools\Run-Tests.ps1' -ProjectDir $t.P -Bundle $t.B 2>&1
    $summary = ($testOut | Where-Object { $_ -match 'OHOS_REPORT_RESULT' }) -join ''
    if (-not $summary) { $summary = 'NO RESULT' }
    $results += [pscustomobject]@{ Project = $name; Build = $buildResult; Test = $summary.Trim() }
    Write-Output ("{0} | {1} | {2}" -f $name, $buildResult, $summary.Trim())
}

Write-Output ''
Write-Output '==== SUMMARY ===='
$results | ForEach-Object { Write-Output ("{0,-26} {1,-6} {2}" -f $_.Project, $_.Build, $_.Test) }
