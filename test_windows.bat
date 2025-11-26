@echo off
setlocal EnableDelayedExpansion

REM ====================================================================
REM WinLink-FYP - Windows Testing & Launch Script
REM Enhanced Desktop Distributed Computing Platform
REM ====================================================================

title WinLink-FYP Testing Suite

cls
echo.
echo  ========================================
echo         W I N L I N K - F Y P
echo         Distributed Computing
echo  ========================================
echo.
echo  Distributed Computing Platform - Windows Testing
echo  ======================================================== 
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Available Testing and Launch Options:
echo.
echo  [1] Launch Main Application (Role Selection)
echo  [2] Launch Master UI Directly  
echo  [3] Launch Worker UI Directly
echo  [4] Setup Environment (Install Dependencies)
echo  [5] Setup Security (Generate Certificates)
echo  [6] Run Security Tests
echo  [7] Run System Performance Test
echo  [8] Clean Project (Remove Cache Files)
echo  [9] Show System Information
echo  [0] Exit
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" (
    call :launch_main
) else if "%choice%"=="2" (
    call :launch_master
) else if "%choice%"=="3" (
    call :launch_worker
) else if "%choice%"=="4" (
    call :setup_environment
) else if "%choice%"=="5" (
    call :setup_security
) else if "%choice%"=="6" (
    call :run_security_tests
) else if "%choice%"=="7" (
    call :run_performance_test
) else if "%choice%"=="8" (
    call :clean_project
) else if "%choice%"=="9" (
    call :show_system_info
) else if "%choice%"=="0" (
    echo Goodbye!
    timeout /t 2 >nul
    exit /b 0
) else (
    echo Invalid choice. Launching main application...
    timeout /t 2 >nul
    call :launch_main
)

echo.
echo Operation completed!
timeout /t 3 >nul
exit /b 0

REM ====================================================================
REM Functions
REM ====================================================================

:launch_main
    echo.
    echo Starting WinLink Main Application...
    echo Opening role selection interface...
    python launch_enhanced.py
    goto :eof

:launch_master
    echo.
    echo Starting Master UI...
    echo Launching distributed computing master node...
    cd /d "%~dp0"
    python master\master_ui.py
    goto :eof

:launch_worker
    echo.
    echo Starting Worker UI...
    echo Launching distributed computing worker node...
    cd /d "%~dp0"
    python worker\worker_ui.py
    goto :eof

:setup_environment
    echo.
    echo Setting up WinLink environment...
    echo Installing Python dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements
        pause
        goto :eof
    )
    echo Environment setup completed!
    pause
    goto :eof

:setup_security
    echo.
    echo Setting up security certificates...
    if exist "windows_setup_certificates.py" (
        python windows_setup_certificates.py
        echo Security certificates generated!
    ) else (
        echo Certificate setup script not found
        echo Security features may be limited
    )
    pause
    goto :eof

:run_security_tests
    echo.
    echo Running security and system tests...
    if exist "test_windows_security.py" (
        python test_windows_security.py
        echo Security tests completed!
    ) else (
        echo Security test script not found
    )
    pause
    goto :eof

:run_performance_test
    echo.
    echo Running system performance test...
    echo Testing CPU, memory, and network capabilities...
    python -c "import psutil, time, socket; print('System Performance Report'); print('=' * 40); print(f'CPU Cores: {psutil.cpu_count()}'); print(f'CPU Usage: {psutil.cpu_percent(interval=1):.1f}%%'); print(f'Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB'); print(f'Memory Available: {psutil.virtual_memory().available / (1024**3):.2f} GB'); print(f'Memory Usage: {psutil.virtual_memory().percent:.1f}%%'); print(f'Disk Free: {psutil.disk_usage(\".\").free / (1024**3):.2f} GB'); print('Performance test completed!')"
    pause
    goto :eof

:clean_project
    echo.
    echo Cleaning project files...
    echo Removing cache and temporary files...
    
    REM Remove Python cache
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"
    for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f"
    
    REM Remove other cache files
    if exist ".pytest_cache" rd /s /q ".pytest_cache"
    if exist "*.log" del /q "*.log"
    if exist "temp" rd /s /q "temp"
    if exist "*.tmp" del /q "*.tmp"
    
    echo Project cleaned successfully!
    pause
    goto :eof

:show_system_info
    echo.
    echo WinLink-FYP System Information
    echo ===============================
    python --version 2>nul || echo Python: Not installed
    echo Platform: Windows
    echo Project: WinLink-FYP
    echo.
    echo Project Structure:
    if exist "main.py" echo [OK] main.py (Main application)
    if exist "role_select.py" echo [OK] role_select.py (Role selection)
    if exist "master\master_ui.py" echo [OK] master\master_ui.py (Master interface)
    if exist "worker\worker_ui.py" echo [OK] worker\worker_ui.py (Worker interface)
    if exist "core\" echo [OK] core\ (Core modules)
    if exist "assets\" echo [OK] assets\ (Assets and styles)
    if exist "requirements.txt" echo [OK] requirements.txt (Dependencies)
    echo.
    pause
    goto :eof