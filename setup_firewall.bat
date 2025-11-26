@echo off
REM Quick Firewall Setup for WinLink
REM Run this as Administrator on BOTH Master and Worker PCs

echo ========================================
echo WinLink Firewall Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Must run as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [INFO] Configuring Windows Firewall...
echo.

REM Remove old rules if they exist
netsh advfirewall firewall delete rule name="WinLink" >nul 2>&1

REM Add inbound rule for all ports 3000-3100 (Worker ports)
echo Adding rule for Worker ports (3000-3100)...
netsh advfirewall firewall add rule name="WinLink" dir=in action=allow protocol=TCP localport=3000-3100 enable=yes profile=any

REM Add inbound rule for discovery (UDP 5000)
echo Adding rule for Worker discovery (UDP 5000)...
netsh advfirewall firewall add rule name="WinLink" dir=in action=allow protocol=UDP localport=5000 enable=yes profile=any

REM Add outbound rules
echo Adding outbound rules...
netsh advfirewall firewall add rule name="WinLink" dir=out action=allow protocol=TCP enable=yes profile=any
netsh advfirewall firewall add rule name="WinLink" dir=out action=allow protocol=UDP localport=5000 enable=yes profile=any

echo.
echo [SUCCESS] Firewall configured!
echo.
echo You can now run WinLink:
echo   Worker PC: python launch_enhanced.py --role worker
echo   Master PC: python launch_enhanced.py --role master
echo.
pause
