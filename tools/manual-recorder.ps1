param(
    [string]$Hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe',
    [string]$Python = 'C:\Users\zhong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
)

function Get-Bounds([string]$jsonPath, [string]$id) {
    $raw = Get-Content $jsonPath -Raw
    $data = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json
    $script:found = $null
    function Walk($node) {
        if ($null -eq $node) { return }
        if ($node.attributes -and $node.attributes.id -eq $id) {
            $script:found = $node.attributes.bounds
        }
        if ($node.children) { foreach ($c in $node.children) { Walk $c } }
    }
    Walk $data
    return $script:found
}

function Parse-Bounds([string]$b) {
    if (-not $b) { return $null }
    $m = [regex]::Match($b, '\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
    if (-not $m.Success) { return $null }
    return @{
        left = [int]$m.Groups[1].Value
        top = [int]$m.Groups[2].Value
        right = [int]$m.Groups[3].Value
        bottom = [int]$m.Groups[4].Value
    }
}

function Dump([string]$name) {
    & $Hdc shell "uitest dumpLayout -p /data/local/tmp/$name.json" 2>&1 | Out-Null
    & $Hdc file recv "/data/local/tmp/$name.json" "E:\zhikong\$name.json" 2>&1 | Out-Null
}

& $Hdc shell aa force-stop ohos.samples.recorder 2>&1 | Out-Null
& $Hdc shell aa start -b ohos.samples.recorder -a EntryAbility 2>&1 | Out-Null
Start-Sleep -Seconds 3
& $Hdc shell "uitest uiInput click 519 728" 2>&1 | Out-Null
Start-Sleep -Seconds 2
Dump 'm1'
$b = Parse-Bounds (Get-Bounds 'E:\zhikong\m1.json' 'btnRecord')
"btnRecord bounds: $($b.left),$($b.top),$($b.right),$($b.bottom)"
$cx = [int](($b.left + $b.right) / 2); $cy = [int](($b.top + $b.bottom) / 2)
& $Hdc shell "uitest uiInput click $cx $cy" 2>&1 | Out-Null
Start-Sleep -Seconds 4
Dump 'm2'
$f = Parse-Bounds (Get-Bounds 'E:\zhikong\m2.json' 'finishRecord')
"finishRecord bounds: $($f.left),$($f.top),$($f.right),$($f.bottom)"
$fx = [int](($f.left + $f.right) / 2); $fy = [int](($f.top + $f.bottom) / 2)
& $Hdc shell "uitest uiInput click $fx $fy" 2>&1 | Out-Null
Start-Sleep -Seconds 3
Dump 'm3'
$i = Parse-Bounds (Get-Bounds 'E:\zhikong\m3.json' 'audioItem0')
"audioItem0 bounds: $($i.left),$($i.top),$($i.right),$($i.bottom)"
if ($i) {
    $ix = [int]($i.left + 60); $iy = [int](($i.top + $i.bottom) / 2)
    & $Hdc shell "uitest uiInput longClick $ix $iy" 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    Dump 'm4'
    $raw = Get-Content 'E:\zhikong\m4.json' -Raw
    "checkedNum after longClick: " + ([regex]::Matches($raw, 'checkedNum').Count)
}
