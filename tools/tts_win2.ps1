param(
  [string]$Voice = 'Yaoyao',
  [string]$TextFile,
  [string]$OutFile
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime | Out-Null

[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media, ContentType=WindowsRuntime] | Out-Null

$methods = [System.WindowsRuntimeSystemExtensions].GetMethods()
Write-Output ("AsTask overloads: " + (($methods | Where-Object { $_.Name -eq 'AsTask' }).Count))

$asTask = $null
foreach ($m in $methods) {
  if ($m.Name -ne 'AsTask') { continue }
  if (-not $m.IsGenericMethodDefinition) { continue }
  $ps = $m.GetParameters()
  if ($ps.Count -ne 1) { continue }
  $asTask = $m
  break
}
if ($null -eq $asTask) { Write-Output 'NO_AS_TASK'; exit 2 }

function Await-Op($op, $type) {
  $g = $asTask.MakeGenericMethod($type)
  $task = $g.Invoke($null, @($op))
  $task.Wait(-1) | Out-Null
  return $task.Result
}

$text = Get-Content -Path $TextFile -Encoding UTF8 -Raw
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$pick = $null
foreach ($v in [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices) {
  if ($v.DisplayName -like ('*' + $Voice + '*')) { $pick = $v; break }
}
if ($null -eq $pick) { Write-Output 'VOICE_NOT_FOUND'; exit 3 }
$synth.Voice = $pick
Write-Output ('using: ' + $pick.DisplayName)

$type = [Windows.Media.SpeechSynthesis.SpeechSynthesisStream]
$stream = Await-Op ($synth.SynthesizeTextToStreamAsync($text)) $type
$net = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
$fs = [System.IO.File]::Create($OutFile)
$net.CopyTo($fs)
$fs.Close(); $net.Close()
Write-Output ('wrote: ' + (Get-Item $OutFile).Length + ' bytes')
