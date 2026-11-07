param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe',
    [string]$Python = 'C:\Users\zhong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
)

function Now-Ms {
    $v = (& $Hdc shell "date +%s%3N" 2>&1 | Out-String).Trim()
    return [int64]$v
}

function Logs {
    return (& $Hdc shell "hilog -x" 2>&1 | Out-String)
}

function Stamp([string]$text, [string]$pattern) {
    $m = [regex]::Match($text, '(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*' + $pattern)
    if (-not $m.Success) { return $null }
    return $m.Groups[1].Value
}

$script:deviceYear = (& $Hdc shell "date +%Y" 2>&1 | Out-String).Trim()

function To-EpochMs([string]$stamp) {
    $dt = [datetime]::ParseExact("$script:deviceYear-$stamp", 'yyyy-MM-dd HH:mm:ss.fff', $null)
    return [int64](($dt - [datetime]'2000-01-01').TotalMilliseconds)
}

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell aa force-stop ohos.samples.recorder 2>&1 | Out-Null
Start-Sleep -Seconds 1
& $Hdc shell aa start -b ohos.samples.recorder -a EntryAbility 2>&1 | Out-Null
Start-Sleep -Seconds 4
& $Hdc shell "uitest uiInput click 511 736" 2>&1 | Out-Null
Start-Sleep -Seconds 1

$rows = @()
for ($i = 1; $i -le 3; $i++) {
    & $Hdc shell "hilog -r" 2>&1 | Out-Null
    $t0 = Now-Ms
    & $Hdc shell "uitest uiInput click 360 1140" 2>&1 | Out-Null
    Start-Sleep -Milliseconds 2500
    $logs = Logs
    $create = Stamp $logs 'createAudioFile path='
    $enter = if ($create) { (To-EpochMs $create) - $t0 } else { -1 }

    & $Hdc shell "hilog -r" 2>&1 | Out-Null
    $t1 = Now-Ms
    & $Hdc shell "uitest uiInput click 344 1014" 2>&1 | Out-Null
    Start-Sleep -Milliseconds 2500
    $logs = Logs
    $refresh = Stamp $logs 'queryAllAudios count='
    $back = if ($refresh) { (To-EpochMs $refresh) - $t1 } else { -1 }

    & $Hdc shell "hilog -r" 2>&1 | Out-Null
    $t2 = Now-Ms
    & $Hdc shell "uitest uiInput click 360 238" 2>&1 | Out-Null
    Start-Sleep -Milliseconds 2500
    $logs = Logs
    $play = Stamp $logs 'PlayPage ready'
    $playMs = if ($play) { (To-EpochMs $play) - $t2 } else { -1 }

    $rows += [pscustomobject]@{ Round = $i; EnterRecordMs = $enter; BackToListMs = $back; EnterPlayMs = $playMs }
    Write-Output ("round {0}: enterRecord={1}ms backToList={2}ms enterPlay={3}ms" -f $i, $enter, $back, $playMs)
    Start-Sleep -Milliseconds 800
}
