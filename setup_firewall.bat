@echo off
title WinLink Firewall Setup

cls
echo.
echo ========================================
echo     WinLink Firewall Setup
echo ========================================
echo.
echo Administrator rights required
echo Run on BOTH Master and Worker PCs
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator rights required!
    echo.
    echo Please right-click this file and select
    echo "Run as administrator" to continue.
    echo.
    pause
    exit /b 1
)

echo Configuring Windows Firewall...
echo.

netsh advfirewall firewall delete rule name="WinLink" >nul 2>&1

echo [1/4] Adding Worker ports rule (TCP 3000-3100)...
netsh advfirewall firewall add rule name="WinLink" dir=in action=allow protocol=TCP localport=3000-3100 enable=yes profile=any

echo [2/4] Adding discovery rule (UDP 5000)...
netsh advfirewall firewall add rule name="WinLink" dir=in action=allow protocol=UDP localport=5000 enable=yes profile=any

echo [3/4] Adding outbound TCP rules...
netsh advfirewall firewall add rule name="WinLink" dir=out action=allow protocol=TCP enable=yes profile=any

echo [4/4] Adding outbound UDP rules...
netsh advfirewall firewall add rule name="WinLink" dir=out action=allow protocol=UDP localport=5000 enable=yes profile=any

echo.
echo SUCCESS: Firewall configured successfully!
echo.
echo You can now run WinLink:
echo   Worker PC: python launch_enhanced.py --role worker
echo   Master PC: python launch_enhanced.py --role master
echo.
pause
