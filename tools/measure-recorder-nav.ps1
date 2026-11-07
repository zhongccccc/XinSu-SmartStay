param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe',
    [string]$Python = 'C:\Users\zhong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
)

$pkg = 'ohos.samples.recorder'

function Dump([string]$name) {
    & $Hdc shell "uitest dumpLayout -p /data/local/tmp/$name.json" 2>&1 | Out-Null
    & $Hdc file recv "/data/local/tmp/$name.json" "E:\zhikong\$name.json" 2>&1 | Out-Null
}

function Bounds([string]$name, [string]$id) {
    $b = (& $Python 'E:\zhikong\tools\find_text.py' "E:\zhikong\$name.json" $id 2>$null | Out-String).Trim()
    return $b
}

function Center([string]$bounds) {
    $m = [regex]::Match($bounds, '\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
    if (-not $m.Success) { return $null }
    return @{
        X = [int](([int]$m.Groups[1].Value + [int]$m.Groups[3].Value) / 2)
        Y = [int](([int]$m.Groups[2].Value + [int]$m.Groups[4].Value) / 2)
    }
}

function Wait-Id([string]$id, [int]$timeoutMs = 5000) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $timeoutMs) {
        Dump 'probe'
        $b = Bounds 'probe' $id
        if ($b) {
            $sw.Stop()
            return [int]$sw.ElapsedMilliseconds
        }
        Start-Sleep -Milliseconds 100
    }
    $sw.Stop()
    return -1
}

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell aa force-stop $pkg 2>&1 | Out-Null
Start-Sleep -Seconds 2
& $Hdc shell aa start -b $pkg -a EntryAbility 2>&1 | Out-Null
Start-Sleep -Seconds 4
& $Hdc shell "uitest uiInput click 511 736" 2>&1 | Out-Null
Start-Sleep -Seconds 1

# 确保至少 2 条录音
Dump 's0'
if (-not (Bounds 's0' 'audioItem1')) {
    for ($k = 0; $k -lt 2; $k++) {
        Dump 's1'
        $c = Center (Bounds 's1' 'btnRecord')
        if ($c) { & $Hdc shell "uitest uiInput click $($c.X) $($c.Y)" 2>&1 | Out-Null }
        Start-Sleep -Seconds 3
        Dump 's2'
        $c = Center (Bounds 's2' 'finishRecord')
        if ($c) { & $Hdc shell "uitest uiInput click $($c.X) $($c.Y)" 2>&1 | Out-Null }
        Start-Sleep -Seconds 3
    }
}

$results = @()
for ($round = 1; $round -le 3; $round++) {
    Dump 't0'
    $enter = 0
    $c = Center (Bounds 't0' 'btnRecord')
    if ($c) {
        & $Hdc shell "uitest uiInput click $($c.X) $($c.Y)" 2>&1 | Out-Null
        $enter = Wait-Id 'recordDuration' 6000
    }
    Start-Sleep -Milliseconds 1200
    Dump 't1'
    $back = 0
    $c = Center (Bounds 't1' 'finishRecord')
    if ($c) {
        & $Hdc shell "uitest uiInput click $($c.X) $($c.Y)" 2>&1 | Out-Null
        $back = Wait-Id 'btnRecord' 6000
    }
    Start-Sleep -Milliseconds 800
    Dump 't2'
    $play = 0
    $c = Center (Bounds 't2' 'audioItem0')
    if ($c) {
        & $Hdc shell "uitest uiInput click $($c.X) $($c.Y)" 2>&1 | Out-Null
        $play = Wait-Id 'playTime' 6000
    }
    $ret = 0
    & $Hdc shell "uitest uiInput keyEvent Back" 2>&1 | Out-Null
    $ret = Wait-Id 'btnRecord' 6000
    $results += [pscustomobject]@{ Round = $round; EnterRecordPage = $enter; BackToList = $back; EnterPlayPage = $play; BackFromPlay = $ret }
    Write-Output ("round {0}: enterRecord={1}ms backToList={2}ms enterPlay={3}ms backFromPlay={4}ms" -f $round, $enter, $back, $play, $ret)
}

Write-Output ''
$results | ForEach-Object { $_ } | Format-Table -AutoSize | Out-String
