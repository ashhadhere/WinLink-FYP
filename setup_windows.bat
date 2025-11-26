@echo off
title WinLink - Automated Setup

cls
echo.
echo ========================================
echo     WinLink - Windows Setup
echo ========================================
echo.
echo Automated installation and configuration
echo ========================================
echo.

echo 📋 This script will:
echo   - Check and install Python dependencies ^(for host application^)
echo   - Generate TLS certificates ^(for secure communication^)
echo   - Create authentication tokens ^(for security^)
echo   - Run security tests ^(to verify setup^)
echo   - Launch the application
echo.
echo ℹ️  Why packages are needed even with Docker:
echo   - Host GUI Application: PyQt5 for Windows desktop interface
echo   - Docker Management: Python docker package to control containers
echo   - Security: TLS/SSL certificates and authentication on host
echo   - Database: SQLite operations for task history and logs
echo   - Monitoring: System resource monitoring with psutil
echo   - Note: Docker containers are used only for isolated task execution
echo.

echo 🎯 Installation Options:
echo   1. Full Installation ^(with Docker support^)
echo   2. Minimal Installation ^(Windows Job Objects only^)
echo   3. Cancel
echo.

set /p install_choice="Choose installation type (1-3): "

if "%install_choice%"=="3" (
    echo Setup cancelled.
    pause
    exit /b
)

if "%install_choice%"=="2" (
    set MINIMAL_INSTALL=1
    echo ℹ️  Minimal installation selected - Docker will be installed but containerization disabled in config
) else (
    set MINIMAL_INSTALL=0
    echo ℹ️  Full installation selected - includes Docker containerization support
)

echo.
echo 🔧 Step 1: Checking and installing Python dependencies...
echo ========================================================

echo 📦 Checking existing packages...

REM Check for PyQt5
python -c "import PyQt5; print('PyQt5 already installed')" 2>nul && set PYQT5_INSTALLED=1 || set PYQT5_INSTALLED=0

REM Check for psutil  
python -c "import psutil; print('psutil already installed')" 2>nul && set PSUTIL_INSTALLED=1 || set PSUTIL_INSTALLED=0

REM Check for docker
python -c "import docker; print('docker already installed')" 2>nul && set DOCKER_INSTALLED=1 || set DOCKER_INSTALLED=0

REM Check for cryptography
python -c "import cryptography; print('cryptography already installed')" 2>nul && set CRYPTO_INSTALLED=1 || set CRYPTO_INSTALLED=0

REM Check for OpenSSL
python -c "import OpenSSL; print('PyOpenSSL already installed')" 2>nul && set OPENSSL_INSTALLED=1 || set OPENSSL_INSTALLED=0

echo.
echo 📋 Package Status:
if %PYQT5_INSTALLED%==1 (echo    ✅ PyQt5 already installed) else (echo    ❌ PyQt5 needs installation)
if %PSUTIL_INSTALLED%==1 (echo    ✅ psutil already installed) else (echo    ❌ psutil needs installation)
if %DOCKER_INSTALLED%==1 (echo    ✅ docker already installed) else (echo    ⚠️  docker needs installation ^(optional for containerization^))
if %CRYPTO_INSTALLED%==1 (echo    ✅ cryptography already installed) else (echo    ❌ cryptography needs installation)
if %OPENSSL_INSTALLED%==1 (echo    ✅ PyOpenSSL already installed) else (echo    ❌ PyOpenSSL needs installation)

REM Check if all required packages are installed
set ALL_INSTALLED=1
if %PYQT5_INSTALLED%==0 set ALL_INSTALLED=0
if %PSUTIL_INSTALLED%==0 set ALL_INSTALLED=0
if %CRYPTO_INSTALLED%==0 set ALL_INSTALLED=0
if %OPENSSL_INSTALLED%==0 set ALL_INSTALLED=0

if %ALL_INSTALLED%==1 (
    echo.
    echo ✅ All required packages already installed! Skipping installation...
    goto :config_override
)

echo.
echo 📦 Installing packages from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install some packages from requirements.txt
    echo Trying individual package installation...
    
    REM Fallback: Install only missing packages individually
    if %PYQT5_INSTALLED%==0 (
        echo Installing PyQt5...
        python -m pip install "PyQt5>=5.15.0"
    )
    
    if %PSUTIL_INSTALLED%==0 (
        echo Installing psutil...
        python -m pip install "psutil>=5.8.0"
    )
    
    if %CRYPTO_INSTALLED%==0 (
        echo Installing cryptography...
        python -m pip install "cryptography>=3.4.8"
    )
    
    if %OPENSSL_INSTALLED%==0 (
        echo Installing PyOpenSSL...
        python -m pip install "PyOpenSSL>=22.0.0"
    )
    
    if %DOCKER_INSTALLED%==0 (
        echo Installing docker ^(optional^)...
        python -m pip install "docker>=6.0.0" || echo ⚠️  Docker package installation failed - containerization will be disabled
    )
)

echo ✅ Package installation completed!

:config_override
REM Configure containerization based on installation choice
if %MINIMAL_INSTALL%==1 (
    echo.
    echo ⚙️  Configuring minimal installation ^(disabling containerization^)...
    echo # Auto-generated configuration override for minimal installation > config_override.py
    echo DISABLE_CONTAINERS = True >> config_override.py
    echo CONTAINER_FALLBACK_ONLY = True >> config_override.py
    echo # This file disables Docker containerization for minimal installation >> config_override.py
    echo ✅ Containerization disabled for minimal installation
)

:certificates
echo.

echo 🔒 Step 2: Setting up security certificates...
echo ===============================================
python windows_setup_certificates.py

if errorlevel 1 (
    echo ❌ Failed to setup certificates
    pause
    exit /b 1
)

echo ✅ Security certificates generated!
echo.

echo 🧪 Step 3: Running security tests...
echo ====================================
python test_windows_security.py

if errorlevel 1 (
    echo ⚠️  Some tests failed, but continuing with setup...
    echo Check the test output above for any critical issues.
    echo.
) else (
    echo ✅ All security tests passed!
    echo.
)

echo 🎯 Step 4: Choose launch option...
echo ===================================
echo.
echo 1. Launch Desktop Application (Recommended)
echo 2. Launch Master Node only
echo 3. Launch Worker Node only
echo 4. Run Security Demo
echo 5. Exit without launching
echo.

set /p launch_choice="Enter your choice (1-5): "

if "%launch_choice%"=="1" (
    echo.
    echo 🚀 Launching WinLink Desktop Application...
    echo ====================================================
    python launch_enhanced.py
) else if "%launch_choice%"=="2" (
    echo.
    echo 🎯 Launching Master Node...
    echo ===========================
    python launch_enhanced.py --role master
) else if "%launch_choice%"=="3" (
    echo.
    echo ⚡ Launching Worker Node...
    echo ==========================
    python launch_enhanced.py --role worker
) else if "%launch_choice%"=="4" (
    echo.
    echo 🎭 Running Security Demo...
    echo ==========================
    python demo_security.py
    pause
) else (
    echo.
    echo ✅ Setup completed! You can now run the application manually:
    echo.
    echo   python launch_enhanced.py     - Full desktop application
    echo   python main.py               - Basic application
    echo   python demo_security.py      - Security feature demo
    echo.
)

echo.
echo ========================================
echo Setup Completed Successfully!
echo ========================================
echo.
echo For more information:
echo   - Check README.md for usage instructions
echo   - Review security features and configuration
echo   - Use test_windows.bat for testing options
echo.
echo ========================================
echo.
pause