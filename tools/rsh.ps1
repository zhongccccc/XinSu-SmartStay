param([Parameter(Mandatory=$true)][string]$Script)
$env:SSH_ASKPASS = 'E:\zhikong\.tmp\ask\ap.cmd'
$env:SSH_ASKPASS_REQUIRE = 'force'
$env:DISPLAY = 'localhost:0'
$opt = @('-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=NUL','-o','LogLevel=ERROR',
         '-o','PreferredAuthentications=password','-o','PubkeyAuthentication=no','-o','ConnectTimeout=15')
$hostName = 'shiqi@10.243.222.40'
& 'C:\Windows\System32\OpenSSH\scp.exe' @opt $Script "${hostName}:/tmp/__remote.sh"
if ($LASTEXITCODE -ne 0) { "SCP FAILED $LASTEXITCODE"; exit 1 }
& 'C:\Windows\System32\OpenSSH\ssh.exe' @opt $hostName "tr -d '\r' < /tmp/__remote.sh | bash"
exit $LASTEXITCODE
