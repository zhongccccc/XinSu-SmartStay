$port = New-Object System.IO.Ports.SerialPort("COM4", 115200, 'None', 8, 'One')
try {
    $port.ReadTimeout = 500
    $port.Open()
    Write-Output "COM4 opened, listening 4s..."
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $sb = New-Object System.Text.StringBuilder
    while ($sw.Elapsed.TotalSeconds -lt 4) {
        try {
            $ch = $port.ReadExisting()
            if ($ch) { [void]$sb.Append($ch) }
        } catch { Start-Sleep -Milliseconds 150 }
    }
    $port.Close()
    $text = $sb.ToString()
    if ($text.Length -eq 0) {
        Write-Output "  no data received"
    } else {
        Write-Output ("  got " + $text.Length + " chars:")
        $lines = $text -split "[`r`n]+"
        $lines | Where-Object { $_.Trim().Length -gt 0 } | Select-Object -First 20 | ForEach-Object { Write-Output ("    " + $_) }
    }
} catch {
    Write-Output ("  open failed: " + $_.Exception.Message)
} finally {
    if ($port.IsOpen) { $port.Close() }
}
