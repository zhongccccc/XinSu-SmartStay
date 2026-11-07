param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [Parameter(Mandatory = $true)][string]$Bundle,
    [string]$TestModule = 'entry_test',
    [int]$TimeoutMs = 300000
)

$hdc = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe'
$ProjectDir = (Resolve-Path $ProjectDir).Path
$name = Split-Path $ProjectDir -Leaf
$outputs = Join-Path $ProjectDir 'entry\build\default\outputs'
$appHap = Get-ChildItem (Join-Path $outputs 'default') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1
$testHap = Get-ChildItem (Join-Path $outputs 'ohosTest') -Filter '*-signed.hap' -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $appHap) { Write-Output "NO APP HAP: $name"; return }
if (-not $testHap) { Write-Output "NO TEST HAP: $name"; return }

& $hdc uninstall $Bundle 2>&1 | Out-Null
& $hdc install -r $appHap.FullName 2>&1 | Out-Null
$installTest = & $hdc install -r $testHap.FullName 2>&1
$log = Join-Path 'E:\zhikong\tools\test-logs' ($name + '.log')
New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null
& $hdc shell aa test -b $Bundle -m $TestModule -s unittest OpenHarmonyTestRunner -s timeout $TimeoutMs *> $log

$text = Get-Content $log -Raw
$result = ($text -split "`n" | Where-Object { $_ -match 'OHOS_REPORT_RESULT' }) -join ''
$fails = ($text -split "`n" | Where-Object { $_ -match 'Error in |stack=' }) | Select-Object -First 6
Write-Output "=== $name ==="
Write-Output $result
foreach ($f in $fails) { Write-Output ('  ' + $f) }
