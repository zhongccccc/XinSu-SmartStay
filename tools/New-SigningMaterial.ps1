param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [Parameter(Mandatory = $true)][string]$BundleName,
    [string]$Apl = 'normal',
    [string[]]$Acls = @()
)

$ErrorActionPreference = 'Stop'
$ProjectDir = (Resolve-Path $ProjectDir).Path
$signatureDir = Join-Path $ProjectDir 'signature'
$sdkLib = 'C:\Users\zhong\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\lib'
$java = 'D:\Program Files\Huawei\DevEco Studio\jbr\bin\java.exe'
$templateProject = 'D:\XTS\code\SystemFeature\Media\Camera\signature'
$work = 'E:\zhikong\tools\sign_work'
$udid = '4E133F4601B3C782DEE0DFD6D29701E81339CFEDD5C6CBA168ADEC2DA0D74521'

New-Item -ItemType Directory -Path $signatureDir -Force | Out-Null
New-Item -ItemType Directory -Path $work -Force | Out-Null

Copy-Item (Join-Path $templateProject 'camera.p12') (Join-Path $signatureDir 'app.p12') -Force
Copy-Item (Join-Path $templateProject 'camera_app.cer') (Join-Path $signatureDir 'app.cer') -Force
$materialDest = Join-Path $signatureDir 'material'
if (Test-Path $materialDest) { Remove-Item $materialDest -Recurse -Force }
Copy-Item (Join-Path $templateProject 'material') $materialDest -Recurse -Force

$chain = [System.IO.File]::ReadAllText((Join-Path $signatureDir 'app.cer'))
$certs = [regex]::Matches($chain, '-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----') | ForEach-Object { $_.Value }
$leaf = $certs[0].TrimEnd() + "`n"
$ca = $certs[1]
$root = $certs[2]

[System.IO.File]::WriteAllText((Join-Path $work 'app_ca.cer'), $ca + "`n", [System.Text.Encoding]::ASCII)
[System.IO.File]::WriteAllText((Join-Path $work 'root_ca.cer'), $root + "`n", [System.Text.Encoding]::ASCII)

$signTool = Join-Path $sdkLib 'hap-sign-tool.jar'
$keystore = Join-Path $signatureDir 'app.p12'
$profileAlias = 'def-profile-key'
& $java -jar $signTool generate-keypair -keyAlias $profileAlias -keyPwd 123456 -keyAlg ECC -keySize NIST-P-256 -keystoreFile $keystore -keystorePwd 123456 | Out-Null
& $java -jar $signTool generate-profile-cert -keyAlias $profileAlias -keyPwd 123456 `
    -issuer 'C=CN,O=OpenHarmony,OU=OpenHarmony Team,CN=OpenHarmony Application CA' `
    -issuerKeyAlias 'openharmony application ca' -issuerKeyPwd 123456 `
    -subject 'C=CN,O=OpenHarmony,OU=OpenHarmony Team,CN=OpenHarmony Application Profile Debug' `
    -validity 3650 -signAlg SHA384withECDSA `
    -rootCaCertFile (Join-Path $work 'root_ca.cer') -subCaCertFile (Join-Path $work 'app_ca.cer') `
    -keystoreFile $keystore -keystorePwd 123456 -outForm certChain -outFile (Join-Path $work 'profile_chain.cer') | Out-Null

$now = [int][double]::Parse((Get-Date -UFormat %s))
$profile = [ordered]@{
    'version-name' = '2.0.0'
    'version-code' = 2
    'uuid' = 'fe686e1b-3770-4824-a938-961b140a7c98'
    'validity' = [ordered]@{ 'not-before' = $now - 3600; 'not-after' = $now + 315360000 }
    'type' = 'debug'
    'bundle-info' = [ordered]@{
        'developer-id' = 'OpenHarmony'
        'development-certificate' = $leaf
        'bundle-name' = $BundleName
        'apl' = $Apl
        'app-feature' = 'hos_normal_app'
    }
    'acls' = [ordered]@{ 'allowed-acls' = @($Acls) }
    'permissions' = [ordered]@{ 'restricted-permissions' = @() }
    'debug-info' = [ordered]@{
        'device-ids' = @($udid)
        'device-id-type' = 'udid'
    }
    'issuer' = 'pki_internal'
}
[System.IO.File]::WriteAllText((Join-Path $work 'profile.json'), ($profile | ConvertTo-Json -Depth 8), (New-Object System.Text.UTF8Encoding($false)))

$p7b = Join-Path $signatureDir 'app_profile.p7b'
if (Test-Path $p7b) { Remove-Item $p7b -Force }
& $java -jar $signTool sign-profile -keyAlias $profileAlias -keyPwd 123456 `
    -signAlg SHA256withECDSA -mode localSign -profileCertFile (Join-Path $work 'profile_chain.cer') `
    -inFile (Join-Path $work 'profile.json') -keystoreFile $keystore -outFile $p7b -keystorePwd 123456 | Out-Null
if (-not (Test-Path $p7b)) { throw "sign-profile failed for $BundleName" }

$pwdHex = '00000016f85b673291e595292d6ae7df15339d1aff5cf36c64ba022e5a7c6e1106782571184e'
$signingInner = @"
    "signingConfigs": [
      {
        "name": "default",
        "material": {
          "certpath": "./signature/app.cer",
          "keyAlias": "openharmony application release",
          "keyPassword": "$pwdHex",
          "profile": "./signature/app_profile.p7b",
          "signAlg": "SHA256withECDSA",
          "storeFile": "./signature/app.p12",
          "storePassword": "$pwdHex"
        }
      }
    ],
"@

$configPath = Join-Path $ProjectDir 'build-profile.json5'
$config = [System.IO.File]::ReadAllText($configPath)
if ($config -match '"signingConfigs"\s*:\s*\[') {
    $config = [regex]::Replace($config, '"signingConfigs"\s*:\s*\[[\s\S]*?\],', $signingInner)
} else {
    $config = [regex]::Replace($config, '"app"\s*:\s*\{', ('"app": {' + "`r`n" + $signingInner))
}
[System.IO.File]::WriteAllText($configPath, $config, (New-Object System.Text.UTF8Encoding($false)))

Write-Output "signing material ready: $BundleName"
