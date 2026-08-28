@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Download-SourceBackfill.ps1" -Priorities "P0,P1,P2"
set EC=%ERRORLEVEL%
echo.
if not "%EC%"=="0" echo El proceso termino con codigo %EC%.
pause
exit /b %EC%
