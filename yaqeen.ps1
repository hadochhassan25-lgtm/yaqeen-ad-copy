<#
.YAQEEN Agent — Launcher
Run this to start the YAQEEN Ad Copy API locally.
Open yaqeen_client.html in your browser for the full demo.
#>

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ApiFile = Join-Path $ScriptDir "services\yaqeen_ad_api_deploy.py"
$ClientFile = Join-Path $ScriptDir "services\yaqeen_client.html"
$Port = 5000

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       YAQEEN Ad Copy Service v2         ║" -ForegroundColor Cyan
Write-Host "║     AI-Powered Ad Copy Engine           ║" -ForegroundColor Cyan
Write-Host "║     Wallet: 0xD0366D78...d13552         ║" -ForegroundColor Cyan
Write-Host "║     Price: `$0.50 USDC / request          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Flask
try {
    $null = python -c "import flask" 2>$null
} catch {
    Write-Host "[!] Installing Flask..." -ForegroundColor Yellow
    python -m pip install flask
}

# Kill existing process on port
$existing = netstat -ano | Select-String ":${Port} " | Select-String "LISTENING"
if ($existing) {
    $pid = $existing.ToString().Trim().Split()[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Start API server
Write-Host "[+] Starting API on http://localhost:${Port}" -ForegroundColor Green
$job = Start-Job -ScriptBlock {
    param($file)
    python -u $file
} -ArgumentList $ApiFile

Start-Sleep -Seconds 3

# Verify
try {
    $r = Invoke-RestMethod -Uri "http://localhost:${Port}/health" -TimeoutSec 5
    Write-Host "[+] API Status: $($r.status)" -ForegroundColor Green
} catch {
    Write-Host "[!] API failed to start" -ForegroundColor Red
    exit 1
}

# Open demo page
Write-Host "[+] Opening demo page..." -ForegroundColor Green
Start-Process $ClientFile

Write-Host ""
Write-Host "────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  API Endpoints:" -ForegroundColor White
Write-Host "  GET  /            Landing page" -ForegroundColor Gray
Write-Host "  GET  /health      Health check" -ForegroundColor Gray
Write-Host "  GET  /api/sample  Sample ad copy" -ForegroundColor Gray
Write-Host "  POST /api/generate Generate custom ad" -ForegroundColor Gray
Write-Host ""
Write-Host "  Example:" -ForegroundColor White
Write-Host "  curl -X POST http://localhost:${Port}/api/generate \`" -ForegroundColor Gray
Write-Host '    -H "Content-Type: application/json" \' -ForegroundColor Gray
Write-Host '    -d "{\"business\":\"Cafe Casa\",\"audience\":\"Young professionals\",\"industry\":\"Coffee\"}"' -ForegroundColor Gray
Write-Host ""
Write-Host "  Client Demo: $ClientFile" -ForegroundColor Gray
Write-Host "────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Keep running
while ($true) {
    $output = Receive-Job -Job $job
    if ($output) { Write-Host $output }
    Start-Sleep -Seconds 1
}
