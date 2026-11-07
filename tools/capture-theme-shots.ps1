param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe',
    [string]$Python = 'C:\Users\zhong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe',
    [string]$Config = 'E:\zhikong\tools\themes.json'
)

$proj = 'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch'
$shots = Join-Path $proj 'screenshots\devices'
New-Item -ItemType Directory -Path $shots -Force | Out-Null
$cfg = Get-Content $Config -Raw -Encoding UTF8 | ConvertFrom-Json

function Dump([string]$name) {
    & $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
    & $Hdc shell "uitest dumpLayout -p /data/local/tmp/$name.json" 2>&1 | Out-Null
    & $Hdc file recv "/data/local/tmp/$name.json" "E:\zhikong\$name.json" 2>&1 | Out-Null
}

function Click-Text([string]$name, [string]$text) {
    $b = (& $Python 'E:\zhikong\tools\find_text.py' "E:\zhikong\$name.json" $text 2>$null | Out-String).Trim()
    if (-not $b) { return $false }
    $m = [regex]::Match($b, '\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
    if (-not $m.Success) { return $false }
    $x = [int](([int]$m.Groups[1].Value + [int]$m.Groups[3].Value) / 2)
    $y = [int](([int]$m.Groups[2].Value + [int]$m.Groups[4].Value) / 2)
    & $Hdc shell "uitest uiInput click $x $y" 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    return $true
}

& $Hdc shell "power-shell setmode 602" 2>&1 | Out-Null
& $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
& $Hdc shell aa force-stop ohos.example.themeswitch 2>&1 | Out-Null
Start-Sleep -Seconds 2
& $Hdc shell aa start -b ohos.example.themeswitch -a MainAbility 2>&1 | Out-Null
Start-Sleep -Seconds 5

foreach ($item in $cfg.items) {
    & $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
    & $Hdc shell "uitest uiInput click 360 108" 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    Dump 'ts_a'
    Dump 'ts_b'
    if (-not (Click-Text 'ts_b' $item.menu)) {
        Write-Output ('menu item not found: ' + $item.file)
        continue
    }
    Start-Sleep -Seconds 2
    & $Hdc shell "power-shell wakeup" 2>&1 | Out-Null
    Start-Sleep -Seconds 1
    $remote = '/data/local/tmp/theme_shot.jpeg'
    & $Hdc shell "snapshot_display -f $remote" 2>&1 | Out-Null
    $tmp = 'E:\zhikong\theme_shot.jpeg'
    if (Test-Path $tmp) { Remove-Item $tmp -Force }
    & $Hdc file recv $remote $tmp 2>&1 | Out-Null
    $size = 0
    if (Test-Path $tmp) { $size = (Get-Item $tmp).Length }
    if ($size -gt 1000) {
        $dst = Join-Path $shots $item.file
        & $Python 'E:\zhikong\tools\jpeg2png.py' $tmp $dst 2>&1 | Out-Null
        $dsize = 0
        if (Test-Path $dst) { $dsize = (Get-Item $dst).Length }
        Write-Output ($item.file + ' <- ' + $size + ' bytes, png=' + $dsize)
    } else {
        Write-Output ($item.file + ' capture failed (' + $size + ')')
    }
}
