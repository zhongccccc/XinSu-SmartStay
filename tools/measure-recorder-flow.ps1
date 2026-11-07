param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe',
    [string]$Python = 'C:\Users\zhong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
)

$pkg = 'ohos.samples.recorder'

function Dump([string]$name) {
    & $Hdc shell "uitest dumpLayout -p /data/local/tmp/$name.json" 2>&1 | Out-Null
    & $Hdc file recv "/data/local/tmp/$name.json" "E:\zhikong\$name.json" 2>&1 | Out-Null
}

function Find-Id([string]$name, [string]$id) {
    $b = (& $Python 'E:\zhikong\tools\find_text.py' "E:\zhikong\$name.json" $id 2>$null | Out-String).Trim()
    if (-not $b) { return $null }
    $m = [regex]::Match($b, '\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
    if (-not $m.Success) { return $null }
    return @{
        X = [int](([int]$m.Groups[1].Value + [int]$m.Groups[3].Value) / 2)
        Y = [int](([int]$m.Groups[2].Value + [int]$m.Groups[4].Value) / 2)
    }
}

function Logs-Matching([string]$pattern) {
    $out = & $Hdc shell "hilog -x" 2>&1 | Out-String
    return ([regex]::Matches($out, '.*' + $pattern + '.*') | ForEach-Object { $_.Value.Trim() })
}

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell "hilog -r" 2>&1 | Out-Null
& $Hdc shell aa force-stop $pkg 2>&1 | Out-Null
Start-Sleep -Seconds 1
& $Hdc shell aa start -b $pkg -a EntryAbility 2>&1 | Out-Null
Start-Sleep -Seconds 4

Dump 'm0'
$btn = Find-Id 'm0' 'btnRecord'
if (-not $btn) { Write-Output 'btnRecord not found'; exit 1 }
& $Hdc shell "uitest uiInput click $($btn.X) $($btn.Y)" 2>&1 | Out-Null
Start-Sleep -Seconds 3
Dump 'm1'
$dur = Find-Id 'm1' 'recordDuration'
Write-Output ('recordDuration present: ' + [bool]$dur)
& $Hdc shell "hilog -r" 2>&1 | Out-Null
$fin = Find-Id 'm1' 'finishRecord'
if ($fin) {
    & $Hdc shell "uitest uiInput click $($fin.X) $($fin.Y)" 2>&1 | Out-Null
    Start-Sleep -Seconds 3
}
Dump 'm2'
$list = Find-Id 'm2' 'btnRecord'
Write-Output ('back to list: ' + [bool]$list)

foreach ($line in (Logs-Matching 'recordPage ready cost|refreshAudios cost|PlayPage ready cost|createAudioFile path')) {
    Write-Output $line
}
