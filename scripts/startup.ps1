@"
YAQEEN Startup Script — запускает все сервисы при загрузке Windows
====================================================================
Автоматически:
  1. API сервер (Flask + Waitress)
  2. Pinggy TCP tunnel (публичный URL)
  3. Worker daemon (авто-биды и мониторинг)
  4. URL watchdog (обновляет Dealwork listing при смене URL)
  
Установка:
  powershell -File startup.ps1 install
  Это добавит ярлык в shell:startup
"@
param([string]$Action = "start")

$ProjectDir = Split-Path -Parent $PSScriptRoot
$ServicesDir = Join-Path $ProjectDir "services"
$ScriptsDir = Join-Path $ProjectDir "scripts"
$MemoryDir = Join-Path $ProjectDir "memory"
$Python = "python"

# Ensure directories
if (-not (Test-Path $MemoryDir)) { New-Item -ItemType Directory -Path $MemoryDir -Force | Out-Null }

function Log {
    param([string]$Msg)
    $t = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$t] $Msg"
    Write-Host $line
    Add-Content -Path (Join-Path $MemoryDir "startup.log") -Value $line
}

function Start-API {
    Log "Starting API server..."
    $logOut = Join-Path $MemoryDir "api_stdout.log"
    $logErr = Join-Path $MemoryDir "api_stderr.log"
    Start-Process -WindowStyle Hidden -FilePath $Python -ArgumentList "$ServicesDir\yaqeen_ad_api_deploy.py" -RedirectStandardOutput $logOut -RedirectStandardError $logErr
    Log "API server started"
}

function Start-Tunnel {
    Log "Starting Pinggy tunnel..."
    $logFile = Join-Path $MemoryDir "tunnel_manager.log"
    Start-Process -WindowStyle Hidden -FilePath $Python -ArgumentList "$ScriptsDir\tunnel_manager_v4.py", "5000" -RedirectStandardOutput $logFile
    Log "Tunnel manager started (v4)"
}

function Start-Worker {
    Log "Starting worker daemon..."
    $logFile = Join-Path $MemoryDir "worker_daemon.log"
    Start-Process -WindowStyle Hidden -FilePath $Python -ArgumentList "$ScriptsDir\worker_daemon.py" -RedirectStandardOutput $logFile
    Log "Worker daemon started"
}

function Install-Startup {
    $targetDir = [Environment]::GetFolderPath("Startup")
    $shortcutPath = Join-Path $targetDir "YAQEEN_Startup.lnk"
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-NoLogo -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`" start"
    $shortcut.WorkingDirectory = $ProjectDir
    $shortcut.Description = "YAQEEN Agent - auto-start all services"
    $shortcut.Save()
    Log "Startup shortcut installed to: $shortcutPath"
    Write-Host "✅ Startup installed. Services will start automatically on boot."
}

function Remove-Startup {
    $targetDir = [Environment]::GetFolderPath("Startup")
    $shortcutPath = Join-Path $targetDir "YAQEEN_Startup.lnk"
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Log "Startup shortcut removed"
        Write-Host "✅ Startup shortcut removed."
    } else {
        Write-Host "No startup shortcut found."
    }
}

switch ($Action) {
    "start" {
        Log "Starting all YAQEEN services..."
        Start-API
        Start-Sleep 5
        Start-Tunnel
        Start-Sleep 3
        Start-Worker
        Log "All services started"
    }
    "install" {
        Install-Startup
    }
    "remove" {
        Remove-Startup
    }
    default {
        Write-Host "Usage: powershell -File startup.ps1 [start|install|remove]"
    }
}
