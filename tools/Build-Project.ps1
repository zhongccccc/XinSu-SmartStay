param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [switch]$TestTarget
)

$ProjectDir = (Resolve-Path $ProjectDir).Path
$env:DEVECO_SDK_HOME = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk'
$env:JAVA_HOME = 'D:\Program Files\Huawei\DevEco Studio\jbr'
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
$node = 'D:\Program Files\Huawei\DevEco Studio\tools\node\node.exe'
$wrapper = 'D:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.js'
$log = Join-Path 'E:\zhikong\tools\build-logs' ((Split-Path $ProjectDir -Leaf) + $(if ($TestTarget) { '-test' } else { '' }) + '.log')
New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null

Push-Location $ProjectDir
try {
    if ($TestTarget) {
        & $node $wrapper --mode module -p module=entry@ohosTest -p product=default -p buildMode=debug assembleHap --no-daemon *> $log
    } else {
        & $node $wrapper --mode module -p product=default -p buildMode=debug assembleHap --no-daemon *> $log
    }
} finally {
    Pop-Location
}

$text = Get-Content $log -Raw
if ($text -match 'BUILD SUCCESSFUL') {
    Write-Output 'BUILD SUCCESSFUL'
} else {
    Write-Output 'BUILD FAILED'
    $lines = Get-Content $log
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'Error Message|COMPILE RESULT') {
            $lines[$i]
            if ($i + 1 -lt $lines.Count) { $lines[$i + 1] }
        }
    }
}
