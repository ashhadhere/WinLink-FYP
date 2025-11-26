# WinLink — Distributed Computing Platform

**WinLink is a distributed desktop application for Windows that enables secure task distribution between master and worker PCs. It features TLS encryption, authentication, process isolation, and real-time monitoring.**

## 🚀 Key Features

### Master PC Capabilities:

- **Task Creation & Dispatch**: Create Python tasks using built-in templates or custom code
- **Worker Management**: Connect to multiple workers across the network
- **Real-time Monitoring**: Monitor CPU, memory, and disk usage on all connected workers
- **Task Queue Management**: View task progress, status, and execution logs
- **Automatic Worker Discovery**: UDP broadcast for discovering workers on local network

### Worker PC Capabilities:

- **Task Execution**: Receive and execute Python tasks from master
- **Resource Sharing**: Configure CPU and memory limits
- **Status Reporting**: Report task progress and completion back to master
- **System Monitoring**: Real-time system resource information
- **Execution Logging**: Capture and display task output and errors

### Security Features:

- **TLS Encryption**: End-to-end encrypted communication with SSL/TLS
- **Token Authentication**: HMAC-based authentication system
- **Process Isolation**: Windows Job Objects for secure task execution
- **Resource Limits**: Memory and CPU constraints for safety
- **Optional Containerization**: Docker support for maximum isolation (requires Docker Desktop)

### Technical Features:

- **JSON-over-TCP Protocol**: Reliable communication between master and workers
- **Automatic Retry Logic**: 3-attempt connection retry with delays for reliability
- **TCP Keep-Alive**: Optimized socket configuration for responsive communication
- **Smart Port Binding**: Automatic retry on port conflicts with error handling
- **Multi-threading**: Concurrent task execution and UI responsiveness
- **Modern GUI**: PyQt5-based interface with system tray integration
- **Task Templates**: Pre-built templates for common computing tasks
- **Persistent Storage**: SQLite database for task history and logs

## 📋 System Requirements

- Windows 10/11 (x64)
- Python 3.8+ (3.9+ recommended)
- 4GB RAM minimum (8GB recommended)
- 100MB free disk space
- Windows PowerShell 5.1+ (included in Windows)
- Docker Desktop for Windows (optional, for containerization)

## 🔧 Setup

### Automated Setup (Recommended)

1. Clone the repository:

```powershell
git clone https://github.com/ashhadhere/WinLink-FYP.git
cd WinLink-FYP
```

2. Run the automated setup:

```powershell
.\setup_windows.bat
```

This will automatically:

- Install all dependencies
- Generate TLS certificates
- Create authentication tokens
- Run security tests
- Launch the application

### Manual Setup

1. Clone the repository:

```powershell
git clone https://github.com/ashhadhere/WinLink-FYP.git
cd WinLink-FYP
```

2. Create virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Generate security certificates:

```powershell
python windows_setup_certificates.py
```

5. Run tests to verify setup:

```powershell
python test_windows_security.py
```

### Firewall Configuration (Required)

Run as Administrator on **BOTH Master and Worker PCs**:

```powershell
.\setup_firewall.bat
```

This configures Windows Firewall to allow WinLink network communication. **Without this step, Master will NOT be able to connect to Worker!**

## 🚀 Running WinLink

### Launch the Application:

**Enhanced Launcher (Recommended):**

```powershell
python launch_enhanced.py
```

**Direct Role Selection:**

```powershell
# Master node
python launch_enhanced.py --role master

# Worker node
python launch_enhanced.py --role worker
```

**Alternative Entry Point:**

```powershell
python main.py
```

### Quick Testing:

```powershell
.\test_windows.bat
```

## 📖 Usage Guide

### Master PC:

1. Launch WinLink and select "Master" role
2. Wait 10-15 seconds for worker discovery
3. Connect to workers:
   - **Auto-discovery**: Select from "Discovered Workers" list → Click "Connect Selected"
   - **Manual**: Enter Worker's IP:Port → Click "Connect to Worker"
4. Create tasks using templates or custom Python code
5. Submit tasks and monitor progress in the Task Queue

### Worker PC:

1. Launch WinLink and select "Worker" role
2. Configure resource limits (CPU and memory)
3. Click "Start Worker"
4. Copy the displayed IP:Port and share with Master
5. Monitor task execution in the log panel

### Message Protocol

**Task Submission (Master → Worker):**

```json
{
  "type": "task_submit",
  "task_id": "1234",
  "metadata": { "name": "Example Task" },
  "code": "print('Hello from worker')",
  "resources": { "max_cpu": 50, "max_memory_mb": 512 }
}
```

**Task Update (Worker → Master):**

```json
{
  "type": "task_update",
  "task_id": "1234",
  "status": "running",
  "progress": 42,
  "stdout": "Partial output..."
}
```

## 📁 Project Structure

```
WinLink-FYP/
├── core/                       # Core functionality
│   ├── network.py             # JSON-over-TCP protocol
│   ├── secure_network.py      # TLS encryption & authentication
│   ├── task_manager.py        # Task scheduling & tracking
│   ├── task_executor.py       # Task execution engine
│   ├── container_task_executor.py  # Docker container support
│   ├── scheduler.py           # Advanced scheduling
│   ├── database.py            # SQLite persistence
│   ├── security.py            # Security utilities
│   └── config.py              # Configuration management
├── master/                     # Master node UI
│   └── master_ui.py
├── worker/                     # Worker node UI
│   └── worker_ui.py
├── ui/                         # UI components
│   └── modern_components.py
├── assets/                     # Resources
│   └── styles.py
├── ssl/                        # TLS certificates (auto-generated)
├── secrets/                    # Authentication tokens (auto-generated)
├── data/                       # SQLite database
├── logs/                       # Application logs
├── main.py                     # Entry point with role selection
├── launch_enhanced.py          # Enhanced launcher
├── requirements.txt            # Dependencies
├── setup_windows.bat           # Automated setup script
├── setup_firewall.bat          # Firewall configuration
└── WinLink.spec                # PyInstaller spec for builds
```

## 🔧 Troubleshooting

### Connection Issues

**If Master cannot connect to Worker:**

1. **Verify firewall configuration** (most common issue):

```powershell
# Run as Administrator on BOTH PCs
.\setup_firewall.bat
```

2. **Check network connectivity:**

```powershell
# From Master PC, ping Worker IP
ping <worker-ip>
```

3. **Ensure correct startup order:**

   - Start Worker PC first → Click "Start Worker"
   - Wait 10-15 seconds for broadcast to stabilize
   - Start Master PC → Connect to worker

4. **Verify same network:**
   - Both PCs must be on same WiFi/LAN
   - Check IP addresses are in same subnet (e.g., 192.168.1.x)
   - Disable VPN if active

### Common Error Messages

**"Connection timed out"**

- Cause: Firewall blocking connection (90% of cases)
- Solution: Run `setup_firewall.bat` as Administrator on both PCs

**"Port already in use"**

- Cause: Previous WinLink instance still running
- Solution:
  ```powershell
  taskkill /F /IM python.exe /T
  ```

**"Certificate verification failed"**

- Cause: Missing or invalid SSL certificates
- Solution:
  ```powershell
  python windows_setup_certificates.py
  ```

### Best Practices

1. Always start Worker PC first
2. Wait 10-15 seconds after starting Worker before connecting
3. Use auto-discovery when possible
4. Check console output for detailed error messages
5. Ensure both PCs have firewall rules configured

### Getting Help

If issues persist:

1. Check `logs/` directory for detailed error logs
2. Run `python test_windows_security.py` to verify setup
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

## 🏗️ Building for Production

To create a standalone executable for distribution:

```powershell
python build_exe.py
```

This creates a `WinLink_Production/` folder with:

- Standalone executable (no Python required)
- All necessary dependencies bundled
- Configuration scripts
- User documentation

See `PACKAGING_GUIDE.md` for detailed build and deployment instructions.
