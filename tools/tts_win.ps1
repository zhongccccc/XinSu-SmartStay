param(
  [Parameter(Mandatory=$true)][string]$Voice,
  [Parameter(Mandatory=$true)][string]$TextFile,
  [Parameter(Mandatory=$true)][string]$OutFile,
  [double]$Rate = 1.0
)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
  $_.GetParameters()[0].ParameterType.FullName -like '*IAsyncOperation*'
})[0]

function Await($op, $type) {
  $t = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
  $t.Wait(-1) | Out-Null
  return $t.Result
}

[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media, ContentType=WindowsRuntime] | Out-Null

$text = Get-Content -Path $TextFile -Encoding UTF8 -Raw
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$all = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices
$pick = $null
foreach ($v in $all) {
  if ($v.DisplayName -like ('*' + $Voice + '*')) { $pick = $v; break }
}
if ($null -eq $pick) {
  Write-Output "VOICE_NOT_FOUND"
  foreach ($v in $all) { Write-Output ("  have: " + $v.DisplayName) }
  exit 1
}
$synth.Voice = $pick
Write-Output ("using: " + $pick.DisplayName)

$stream = Await ($synth.SynthesizeTextToStreamAsync($text)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
$netStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
$fs = [System.IO.File]::Create($OutFile)
$netStream.CopyTo($fs)
$fs.Close()
$netStream.Close()
Write-Output ("wrote: " + $OutFile + "  " + (Get-Item $OutFile).Length + " bytes")
