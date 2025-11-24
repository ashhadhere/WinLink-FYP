# 🖥️ WinLink – Distributed Computing Desktop App

WinLink is an advanced desktop application built with Python and PyQt5 that enables **distributed computing** across multiple PCs over LAN. A Master PC can distribute computational tasks to Worker PCs, utilizing their unused resources to perform heavy computations efficiently.

---

## ✨ Features

### 🎛️ Master PC Capabilities

- **Task Management**: Create and distribute computational tasks to worker PCs
- **Worker Monitoring**: Real-time monitoring of connected worker PCs
- **Resource Tracking**: Monitor CPU, RAM, and disk usage across all workers
- **Task Templates**: Pre-built templates for common computational tasks
- **Custom Code Execution**: Execute custom Python code on worker machines
- **Task Queue Management**: Automatic task distribution and load balancing

### 💼 Worker PC Capabilities

- **Task Execution**: Execute computational tasks safely in isolated environments
- **Resource Sharing**: Share CPU, memory, and storage resources
- **Resource Limits**: Configure maximum resource usage per task
- **Real-time Monitoring**: Monitor system resources and task execution
- **Task Logging**: Comprehensive logging of all task executions
- **Security**: Safe execution environment with restricted imports

### 🔧 Built-in Task Templates

1. **Fibonacci Calculation** - Calculate large Fibonacci numbers
2. **Prime Number Check** - Check if large numbers are prime
3. **Matrix Multiplication** - Perform matrix operations
4. **Data Analysis** - Statistical analysis of numerical datasets

---

## 🚀 Getting Started

### Prerequisites

- Windows 10/11
- Python 3.7 or higher
- Network connectivity between PCs

### Installation

1. **Clone or download this repository**

```bash
git clone <repository-url>
cd WinLink-FYP
```

2. **Install required dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the application**

```bash
python main.py
```

---

## 📖 How to Use

### Setting Up a Worker PC

1. **Launch the Application**

   - Run `python main.py`
   - Select "Worker PC" from the role selection screen

2. **Configure Worker Settings**

   - Enter a port number (e.g., 5001)
   - Choose which resources to share (CPU, Memory, Storage)
   - Set resource limits (Max CPU %, Max Memory per task)

3. **Start Worker Service**
   - Click "Start Worker Service"
   - Note the IP:Port combination displayed
   - Worker is now ready to receive tasks

### Setting Up a Master PC

1. **Launch the Application**

   - Run `python main.py`
   - Select "Master PC" from the role selection screen

2. **Connect to Workers**

   - Enter Worker IP and Port in the "Add Worker" section
   - Click "Connect" to establish connection
   - Repeat for multiple workers

3. **Create and Submit Tasks**

   - Choose a task template from the dropdown
   - Modify task code if needed
   - Adjust task data (JSON format)
   - Click "Submit Task" to send to workers

4. **Monitor Task Execution**
   - View task queue and status in real-time
   - Monitor worker resource usage
   - See task results and execution times

---

## 🏗️ Architecture

### Core Components

```
WinLink-FYP/
├── core/                    # Core distributed computing modules
│   ├── task_manager.py      # Task creation and management
│   ├── task_executor.py     # Safe task execution engine
│   └── network.py           # Network communication protocol
├── master/                  # Master PC interface
│   └── master_ui_enhanced.py # Enhanced master UI
├── worker/                  # Worker PC interface
│   └── worker_ui_enhanced.py # Enhanced worker UI
├── assets/                  # UI styles and assets
│   └── styles.py            # Application styling
├── main.py                  # Application entry point
└── role_select.py           # Role selection screen
```

### Communication Protocol

- **TCP Socket Communication**: Reliable connection between Master and Workers
- **JSON Message Format**: Structured data exchange
- **Message Types**: Task requests, resource data, heartbeats, results
- **Automatic Reconnection**: Handles network interruptions gracefully

### Security Features

- **Sandboxed Execution**: Tasks run in isolated Python namespaces
- **Resource Limits**: CPU and memory usage restrictions per task
- **Safe Imports**: Only whitelisted Python modules allowed
- **Timeout Protection**: Tasks have maximum execution time limits

---

## 🔧 Technical Specifications

### Task Execution Environment

- **Execution Timeout**: 5 minutes maximum per task
- **Memory Limit**: 512MB maximum per task (configurable)
- **Allowed Modules**: math, statistics, random, datetime, json, re
- **Safe Built-ins**: Core Python functions only, no file system access

### Performance Features

- **Parallel Processing**: Multiple tasks can run simultaneously
- **Load Balancing**: Tasks distributed across available workers
- **Resource Monitoring**: Real-time system resource tracking
- **Automatic Cleanup**: Completed tasks are automatically cleaned up

### Network Requirements

- **Protocol**: TCP/IP
- **Ports**: User-configurable (default: 5001+)
- **Bandwidth**: Minimal - only task code and results transferred
- **Latency**: Low latency LAN recommended for best performance

---

## 📊 Use Cases

### 🧮 Scientific Computing

- Mathematical simulations and calculations
- Statistical analysis of large datasets
- Numerical modeling and optimization

### 🔬 Research Applications

- Data processing and analysis
- Algorithm testing and benchmarking
- Parallel computation experiments

### 🏢 Educational Projects

- Distributed systems learning
- Computer networking demonstrations
- Performance comparison studies

### 💻 Development & Testing

- Code execution across different environments
- Performance testing on various hardware
- Distributed application prototyping

---

## 🛠️ Build Executable

To create standalone executables:

```bash
# Install PyInstaller
pip install pyinstaller

# Build Master PC executable
pyinstaller --onefile --windowed --name "WinLink-Master" main.py

# Build Worker PC executable
pyinstaller --onefile --windowed --name "WinLink-Worker" main.py
```

---

## 🔍 Troubleshooting

### Common Issues

**Connection Failed**

- Verify IP addresses and ports
- Check Windows Firewall settings
- Ensure both PCs are on the same network

**Task Execution Errors**

- Check task code syntax
- Verify JSON data format
- Review worker resource limits

**Performance Issues**

- Monitor worker CPU/memory usage
- Reduce task complexity or data size
- Increase worker resource limits

### Firewall Configuration

Windows may block the application. Add firewall exceptions:

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python.exe or the built executable

---

## 📈 Future Enhancements

- **GPU Computing**: CUDA/OpenCL task support
- **Web Interface**: Browser-based management console
- **Task Scheduling**: Advanced scheduling algorithms
- **Fault Tolerance**: Automatic task retry and failover
- **Encryption**: Secure communication protocols
- **Docker Integration**: Containerized task execution

---

## 👨‍💻 Developer Information

**Project**: Final Year Project (FYP)  
**Technology Stack**: Python, PyQt5, Socket Programming, psutil  
**Architecture**: Client-Server with Distributed Computing  
**Platform**: Windows (Linux/Mac compatible with minor modifications)

---

## 📜 License

This project is developed as a Final Year Project (FYP) for educational purposes.

---

**WinLink** - Transforming low-spec PCs into high-performance distributed computing clusters! 🚀
