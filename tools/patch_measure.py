import io
p = r'E:\zhikong\tools\measure-recorder-hilog.ps1'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''function To-EpochMs([string]$stamp) {
    $dt = [datetime]::ParseExact($stamp, 'MM-dd HH:mm:ss.fff', $null)
    $origin = [datetime]::new(2000, 1, 1, 0, 0, 0)
    if ($dt -lt $origin) { $dt = $dt.AddYears(2000 - $dt.Year) }
    return [int64](($dt - [datetime]'2000-01-01').TotalMilliseconds)
}''','''$script:deviceYear = (& $Hdc shell "date +%Y" 2>&1 | Out-String).Trim()

function To-EpochMs([string]$stamp) {
    $dt = [datetime]::ParseExact("$script:deviceYear-$stamp", 'yyyy-MM-dd HH:mm:ss.fff', $null)
    return [int64](($dt - [datetime]'2000-01-01').TotalMilliseconds)
}''')
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('patched')
