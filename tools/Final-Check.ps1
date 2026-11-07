$projects = @(
    'D:\XTS\code\SystemFeature\Notification\Publish',
    'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch',
    'D:\XTS\code\SystemFeature\Media\GamePuzzle',
    'D:\XTS\code\SystemFeature\WindowManagement\WindowManage',
    'D:\XTS\code\SystemFeature\Security\CertificateFramework',
    'D:\XTS\code\SystemFeature\Media\VoiceCallDemo',
    'D:\XTS\code\SystemFeature\Media\Recorder',
    'D:\XTS\code\SystemFeature\Media\MusicPlayer'
)

foreach ($p in $projects) {
    $name = Split-Path $p -Leaf
    $sig = Join-Path $p 'signature'
    $files = if (Test-Path $sig) { (Get-ChildItem $sig -File | Select-Object -ExpandProperty Name) -join ',' } else { 'MISSING' }
    $hap = Get-ChildItem (Join-Path $p 'entry\build\default\outputs\default') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1
    $thap = Get-ChildItem (Join-Path $p 'entry\build\default\outputs\ohosTest') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1
    $docs = (Test-Path (Join-Path $p 'README_zh.md')) -and (Test-Path (Join-Path $p 'ohosTest.md'))
    $bp = Get-Content (Join-Path $p 'build-profile.json5') -Raw
    $sdkOk = ($bp -match '"compileSdkVersion"\s*:\s*"26\.0\.0"') -and ($bp -match '"compatibleSdkVersion"\s*:\s*"26\.0\.0"') -and ($bp -match '"targetSdkVersion"\s*:\s*"26\.0\.0"')
    $runtimeOk = $bp -match '"runtimeOS"\s*:\s*"OpenHarmony"'
    $signedOk = $bp -match 'signingConfigs\s*:\s*\[\s*\{'
    Write-Output ("{0,-26} sdk={1} runtime={2} signing={3} appHap={4} testHap={5} docs={6}" -f `
        $name, $sdkOk, $runtimeOk, $signedOk, [bool]$hap, [bool]$thap, $docs)
    Write-Output ("  signature: {0}" -f $files)
}
