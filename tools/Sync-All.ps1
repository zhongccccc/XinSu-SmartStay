param(
    [string[]]$Projects = @(
        'D:\XTS\code\SystemFeature\Notification\Publish',
        'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch',
        'D:\XTS\code\SystemFeature\Media\GamePuzzle',
        'D:\XTS\code\SystemFeature\WindowManagement\WindowManage',
        'D:\XTS\code\SystemFeature\Security\CertificateFramework',
        'D:\XTS\code\SystemFeature\Media\VoiceCallDemo',
        'D:\XTS\code\SystemFeature\Media\Recorder',
        'D:\XTS\code\SystemFeature\Media\MusicPlayer'
    )
)

$env:DEVECO_SDK_HOME = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk'
$env:JAVA_HOME = 'D:\Program Files\Huawei\DevEco Studio\jbr'
$node = 'D:\Program Files\Huawei\DevEco Studio\tools\node\node.exe'
$wrapper = 'D:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.js'

foreach ($p in $Projects) {
    $name = Split-Path $p -Leaf
    Push-Location $p
    try {
        $out = & $node $wrapper --sync --no-daemon 2>&1 | Out-String
        $code = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    $hasError = $out -match 'ERROR|Error Message'
    if ($code -eq 0 -and -not $hasError) {
        Write-Output "$name : SYNC OK (exit=$code)"
    } else {
        $err = ($out -split "`n" | Where-Object { $_ -match 'Error Message|ERROR' } | Select-Object -First 2) -join ' | '
        Write-Output "$name : SYNC FAIL (exit=$code) -> $err"
    }
}
