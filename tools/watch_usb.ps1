$end = (Get-Date).AddMinutes(4)
$seen = @{}
while ((Get-Date) -lt $end) {
    $devs = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
        Where-Object { $_.FriendlyName -match 'Rockchip|MASKROM|rockusb|USB 设备|Unknown|未知' -or
                       $_.InstanceId -match 'VID_2207' }
    foreach ($d in $devs) {
        $key = $d.InstanceId
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = 1
            "[{0:HH:mm:ss}] 新设备: {1} | {2} | {3}" -f (Get-Date), $d.Status, $d.Class, $d.FriendlyName
        }
    }
    Start-Sleep -Seconds 2
}
if ($seen.Count -eq 0) { "4 分钟内没有检测到任何 Rockchip/MASKROM 设备" }
