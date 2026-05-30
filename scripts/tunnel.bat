@echo off
REM Yaqeen Tunnel Manager - uses pinggy for free public URL
REM This script starts the SSH tunnel and saves the URL
set PORT=5000
set LOGFILE=%USERPROFILE%\Desktop\moltbook-app\memory\tunnel.log
set URLFILE=%USERPROFILE%\Desktop\moltbook-app\memory\public_url.txt

:loop
echo [%DATE% %TIME%] Starting tunnel: pinggy -> localhost:%PORT% >> "%LOGFILE%"
ssh -p 443 -R 0:localhost:%PORT% -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes a.pinggy.io 2>&1 | findstr "pinggy" > "%URLFILE%"
echo [%DATE% %TIME%] Tunnel exited, restarting in 5s... >> "%LOGFILE%"
timeout /t 5 /nobreak > nul
goto loop
