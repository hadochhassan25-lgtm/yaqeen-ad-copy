$scriptPath = Join-Path $PSScriptRoot "services" "telegram_bot.py"
Write-Host "YAQEEN Bot Launcher - Auto-restart on crash"
Write-Host "Press Ctrl+C to stop"
while ($true) {
    Write-Host "$(Get-Date -Format 'HH:mm:ss') Starting bot..."
    try {
        python $scriptPath 2>&1
    } catch {
        Write-Host "Exception: $_"
    }
    Write-Host "$(Get-Date -Format 'HH:mm:ss') Bot stopped. Restarting in 3s..."
    Start-Sleep -Seconds 3
}
