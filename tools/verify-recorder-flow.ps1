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

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell "hilog -r" 2>&1 | Out-Null
& $Hdc shell aa force-stop $pkg 2>&1 | Out-Null
Start-Sleep -Seconds 1
& $Hdc shell aa start -b $pkg -a EntryAbility 2>&1 | Out-Null
Start-Sleep -Seconds 4
Dump 'f0'
$btn = Find-Id 'f0' 'btnRecord'
& $Hdc shell "uitest uiInput click $($btn.X) $($btn.Y)" 2>&1 | Out-Null
Start-Sleep -Seconds 3
Dump 'f1'
& $Hdc shell "snapshot_display -f /data/local/tmp/f1.jpeg" 2>&1 | Out-Null
& $Hdc file recv /data/local/tmp/f1.jpeg 'E:\zhikong\final_record.jpeg' 2>&1 | Out-Null
$fin = Find-Id 'f1' 'finishRecord'
& $Hdc shell "uitest uiInput click $($fin.X) $($fin.Y)" 2>&1 | Out-Null
Start-Sleep -Seconds 3
Dump 'f2'
& $Hdc shell "snapshot_display -f /data/local/tmp/f2.jpeg" 2>&1 | Out-Null
& $Hdc file recv /data/local/tmp/f2.jpeg 'E:\zhikong\final_list.jpeg' 2>&1 | Out-Null

# 播放页
Dump 'f3'
$item = Find-Id 'f3' 'audioItem0'
& $Hdc shell "uitest uiInput click $($item.X) $($item.Y)" 2>&1 | Out-Null
Start-Sleep -Seconds 2
Dump 'f4'
& $Hdc shell "uitest uiInput click 52 117" 2>&1 | Out-Null
Start-Sleep -Seconds 2

# 左滑列表项
Dump 'f5'
$item = Find-Id 'f5' 'audioItem0'
& $Hdc shell "uitest uiInput swipe $($item.X) $($item.Y) 40 $($item.Y) 400" 2>&1 | Out-Null
Start-Sleep -Seconds 1
Dump 'f6'
& $Hdc shell "snapshot_display -f /data/local/tmp/f6.jpeg" 2>&1 | Out-Null
& $Hdc file recv /data/local/tmp/f6.jpeg 'E:\zhikong\final_swipe.jpeg' 2>&1 | Out-Null
Write-Output ('swipe renameButton: ' + [bool](Find-Id 'f6' 'renameAudio0'))

$errs = & $Hdc shell "hilog -x" 2>&1 | Select-String -Pattern 'JsError|TypeError|Unhandled|Exception' | Select-Object -Last 5
if ($errs) { $errs | ForEach-Object { Write-Output $_.Line.Trim() } } else { Write-Output 'no js errors' }
