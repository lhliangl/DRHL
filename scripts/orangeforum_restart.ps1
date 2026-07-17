param(
    [string]$SourceRoot = "D:/Go_project/orangeforum",
    [int]$Port = 9123,
    [string]$Dsn = "postgres://postgres:root@localhost:5432/orangeforum",
    [string]$SecretKey = "DRHLORANGEFORUMSECRETKEY12345678",
    [int]$TimeoutSeconds = 90
)

$ErrorActionPreference = "Stop"

function Get-PortPids([int]$PortNumber) {
    $lines = netstat -ano | Select-String (":" + $PortNumber + "\s")
    foreach ($line in $lines) {
        $parts = ($line.ToString().Trim() -split "\s+")
        if ($parts.Length -ge 5 -and $parts[3] -eq "LISTENING") {
            $pidText = $parts[4]
            if ($pidText -match "^\d+$") { [int]$pidText }
        }
    }
}

$pids = @(Get-PortPids -PortNumber $Port | Select-Object -Unique)
foreach ($processId in $pids) {
    if ($processId -gt 0) {
        & taskkill /PID $processId /F | Out-Null
    }
}
Start-Sleep -Milliseconds 800

$SourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
$command = @"
`$env:ORANGEFORUM_DSN = '$Dsn'
`$env:SECRET_KEY = '$SecretKey'
Set-Location -LiteralPath '$SourceRoot'
& go run . -port $Port -disablelogger
"@

$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
$process = Start-Process -FilePath "powershell" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded) -WindowStyle Hidden -PassThru

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$url = "http://localhost:$Port/forums/localhost/"
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            Write-Output "orangeforum restarted on port $Port with PID $($process.Id)"
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

throw "orangeforum did not become ready on $url within $TimeoutSeconds seconds; started PID $($process.Id)"