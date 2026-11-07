param(
    [Parameter(Mandatory = $true)][string]$ProjectDir
)

$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path $ProjectDir).Path
$projectName = Split-Path $ProjectDir -Leaf

function Set-Text($path, $text) {
    [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
}

function Set-ModelVersion($path) {
    if (-not (Test-Path $path)) { return }
    $text = [System.IO.File]::ReadAllText($path)
    if ($text -match '"modelVersion"\s*:\s*"[^"]*"') {
        $text = [regex]::Replace($text, '"modelVersion"\s*:\s*"[^"]*"', '"modelVersion": "26.0.0"')
    } else {
        $text = [regex]::new('(?m)^\{').Replace($text, "{`r`n  `"modelVersion`": `"26.0.0`",", 1)
    }
    Set-Text $path $text
}

# 0. local.properties
$localProps = Join-Path $ProjectDir 'local.properties'
if (-not (Test-Path $localProps) -or ([System.IO.File]::ReadAllText($localProps) -notmatch 'sdk\.dir')) {
    Set-Text $localProps "sdk.dir=C:/Users/zhong/AppData/Local/OpenHarmony/Sdk`n"
}

# 1. root build-profile.json5
$bpPath = Join-Path $ProjectDir 'build-profile.json5'
$content = [System.IO.File]::ReadAllText($bpPath)
$content = [regex]::Replace($content, '"compileSdkVersion"\s*:\s*"?[^",\r\n]+"?', '"compileSdkVersion": "26.0.0"')
$content = [regex]::Replace($content, '"compatibleSdkVersion"\s*:\s*"?[^",\r\n]+"?', '"compatibleSdkVersion": "26.0.0"')
$content = [regex]::Replace($content, '"targetSdkVersion"\s*:\s*"?[^",\r\n]+"?', '"targetSdkVersion": "26.0.0"')
if ($content -match '"runtimeOS"') {
    $content = [regex]::Replace($content, '"runtimeOS"\s*:\s*"[^"]*"', '"runtimeOS": "OpenHarmony"')
}
if ($content -notmatch '"compileSdkVersion"') {
    $content = [regex]::Replace($content, '("compatibleSdkVersion"\s*:\s*"26\.0\.0")', "`"compileSdkVersion`": `"26.0.0`",`r`n        `$1")
}
if ($content -notmatch '"targetSdkVersion"') {
    $content = [regex]::Replace($content, '("compatibleSdkVersion"\s*:\s*"26\.0\.0")', "`$1,`r`n        `"targetSdkVersion`": `"26.0.0`"")
}
if ($content -notmatch 'buildModeSet') {
    $content = [regex]::Replace($content, '("products"\s*:\s*\[[\s\S]*?\n    \])(\s*)\}', "`$1,`r`n    `"buildModeSet`": [`r`n      {`r`n        `"name`": `"debug`"`r`n      },`r`n      {`r`n        `"name`": `"release`"`r`n      }`r`n    ]`r`n  }")
}
Set-Text $bpPath $content

# 2. hvigorfile.ts (root + modules, choose task type by module type)
$appHvigor = @'
import { appTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: appTasks, /* Built-in plugin of Hvigor. It cannot be modified. */
  plugins: []       /* Custom plugin to extend the functionality of Hvigor. */
}
'@

function New-ModuleHvigor([string]$task) {
    return @"
import { $task } from '@ohos/hvigor-ohos-plugin';

export default {
  system: $task, /* Built-in plugin of Hvigor. It cannot be modified. */
  plugins: []    /* Custom plugin to extend the functionality of Hvigor. */
}
"@
}

Set-Text (Join-Path $ProjectDir 'hvigorfile.ts') $appHvigor
Set-ModelVersion (Join-Path $ProjectDir 'oh-package.json5')

foreach ($moduleDir in (Get-ChildItem $ProjectDir -Directory)) {
    $moduleBp = Join-Path $moduleDir.FullName 'build-profile.json5'
    if (-not (Test-Path $moduleBp)) { continue }

    $moduleJson = Join-Path $moduleDir.FullName 'src\main\module.json5'
    $task = 'hapTasks'
    if (Test-Path $moduleJson) {
        $mj = [System.IO.File]::ReadAllText($moduleJson)
        if ($mj -match '"type"\s*:\s*"har"') { $task = 'harTasks' }
        elseif ($mj -match '"type"\s*:\s*"shared"') { $task = 'sharedTasks' }
    } else {
        $task = 'harTasks'
    }
    Set-Text (Join-Path $moduleDir.FullName 'hvigorfile.ts') (New-ModuleHvigor $task)
    Set-ModelVersion (Join-Path $moduleDir.FullName 'oh-package.json5')
}

# 3. hvigor/hvigor-config.json5, remove wrapper files
$hvigorDir = Join-Path $ProjectDir 'hvigor'
New-Item -ItemType Directory -Path $hvigorDir -Force | Out-Null
$wrapperJs = Join-Path $hvigorDir 'hvigor-wrapper.js'
if (Test-Path $wrapperJs) { Remove-Item $wrapperJs -Force }
Set-Text (Join-Path $hvigorDir 'hvigor-config.json5') "{`n  `"modelVersion`": `"26.0.0`",`n  `"dependencies`": {`n  }`n}`n"
foreach ($f in @('hvigorw', 'hvigorw.bat')) {
    $p = Join-Path $ProjectDir $f
    if (Test-Path $p) { Remove-Item $p -Force }
}

Write-Output "updated: $projectName"
