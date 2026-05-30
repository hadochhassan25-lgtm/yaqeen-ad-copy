param($Port=5000)

$logFile = "$env:USERPROFILE\Desktop\moltbook-app\memory\tunnel.log"
$urlFile = "$env:USERPROFILE\Desktop\moltbook-app\memory\public_url.txt"

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

function Start-Tunnel {
    Write-Log "Connecting to pinggy -> localhost:$Port ..."
    
    $proc = [System.Diagnostics.Process]::Start(@{
        FileName = "ssh"
        Arguments = "-p 443 -R 0:localhost:$Port -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -o ConnectTimeout=10 a.pinggy.io"
        UseShellExecute = $false
        RedirectStandardOutput = $true
        CreateNoWindow = $true
    })
    
    $urlFound = $false
    while (-not $proc.StandardOutput.EndOfStream) {
        $line = $proc.StandardOutput.ReadLine()
        if ($line -match '(http[^\s]+run\.pinggy-free\.link)') {
            $url = $matches[1].Trim()
            Write-Log "PUBLIC URL: $url"
            Set-Content -Path $urlFile -Value $url
            $urlFound = $true
            Write-Log "Tunnel UP and running!"
        }
    }
    
    $proc.WaitForExit()
    Write-Log "Tunnel process exited (code: $($proc.ExitCode))"
}

Write-Log "=== Tunnel Manager Started ==="
while ($true) {
    try {
        Start-Tunnel
    } catch {
        Write-Log "Error: $_"
    }
    Write-Log "Restarting in 5 seconds..."
    Start-Sleep -Seconds 5
}
