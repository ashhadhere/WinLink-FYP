# WinLink — Distributed Python Task Runner (FYP)

**WinLink is a lightweight distributed desktop application that enables task distribution between master and worker PCs through PyQt5 GUIs, where the master sends tasks to remote workers over TCP, and workers execute them and report completion status back with real-time system monitoring.**

This project was developed as a Final Year Project (FYP) to demonstrate distributed computing concepts, remote task dispatch, resource sharing, and system monitoring in an educational environment.

**Repository layout**

- `master/` — Master GUI and logic (`master_ui.py`) for creating tasks, connecting workers, and monitoring the task queue.
- `worker/` — Worker GUI and logic (`worker_ui.py`) that runs the worker service, accepts tasks, and reports status.
- `core/` — Core primitives: networking, task manager, and task executor.
- `assets/` — Shared UI styles and assets.
- `main.py`, `launch_enhanced.py` — Start scripts for the application.

## 🚀 Key Features

### Master PC Capabilities:
- **Task Creation & Dispatch**: Create Python tasks using built-in templates or custom code
- **Worker Management**: Connect to multiple remote workers across the network
- **Real-time Monitoring**: Monitor CPU, memory, and disk usage on all connected workers
- **Task Queue Management**: View task progress, status, and execution logs in real-time
- **Resource Control**: Set CPU and memory limits for each worker

### Worker PC Capabilities:
- **Task Execution**: Receive and execute Python tasks from master
- **Resource Sharing**: Configure CPU and memory limits to share with master
- **Status Reporting**: Report task progress and completion back to master
- **System Monitoring**: Share real-time system resource information
- **Execution Logging**: Capture and display task output and errors

### Technical Features:
- **JSON-over-TCP Protocol**: Simple and reliable communication between master and workers
- **Multi-threading**: Concurrent task execution and UI responsiveness
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Modern GUI**: PyQt5-based interface with animations and system tray integration
- **Task Templates**: Pre-built templates for common computing tasks
- **Safety Features**: Basic sandboxing and resource limits for task execution

Requirements

- Python 3.8+
- See `requirements.txt` (PyQt5, psutil, optional PyInstaller for packaging)

Installation

1. Clone the repository and change to the project folder:

```powershell
git clone <repository-url>
cd WinLink-FYP
```

2. (Optional) Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

Running the app

- Start the Master UI:

```powershell
python main.py
```

- On worker machines, start the Worker UI and configure the port and resource sharing options. Then click `Start Worker` to listen for tasks.

Master UI overview (`master/master_ui.py`)

- Worker management panel: discover/connect to workers, view their current CPU/memory usage, and configured limits.
- Task queue: create tasks from built-in templates or submit custom Python code. The queue displays task name, assigned worker, progress (progress bar), status (with color), and output preview.
- Task creation form supports common templates and direct code entry.

Worker UI overview (`worker/worker_ui.py`)

- Share Resources: set maximum CPU share and memory cap that the worker presents to the Master.
- Execution log: view the live stdout/stderr of tasks run on this worker; responsive sizing for small screens.
- Start/Stop worker controls with clear padding and spacing for accessibility.

Core components (`core/`)

- `network.py`: Implements a small JSON-over-TCP protocol used by Master and Worker to exchange messages (task submission, status updates, heartbeats).
- `task_manager.py`: Tracks tasks on the Master (queued, running, finished) and provides APIs for scheduling/dispatching.
- `task_executor.py`: Runs tasks on the Worker, captures stdout/stderr, reports progress, and enforces basic timeouts.

Message format (example)

- Task submission (Master -> Worker):

```json
{
  "type": "task_submit",
  "task_id": "1234",
  "metadata": {"name": "Example Task"},
  "code": "print('Hello from worker')",
  "resources": {"max_cpu": 50, "max_memory_mb": 512}
}
```

- Task progress update (Worker -> Master):

```json
{
  "type": "task_update",
  "task_id": "1234",
  "status": "running",
  "progress": 42,
  "stdout": "Partial output..."
}
```

Security and sandboxing

This project implements only a prototype-level sandboxing approach (restricted builtins and a module whitelist) for educational purposes. It is NOT safe for running untrusted code in a production environment. Recommended hardening (outside the repo scope):

- Run tasks inside OS-level containers (Docker), restricted VMs, or separate processes with namespace / capability restrictions.
- Use OS user isolation, cgroups, and seccomp policies for Linux.

Packaging

- You can package the GUIs using PyInstaller (see `requirements.txt` for the package). Typical usage:

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Troubleshooting

- If the UI is unresponsive, ensure the Qt event loop is running and background threads report via Qt signals or timers.
- If Workers don't appear in Master, verify firewall/port settings and that Workers are started and listening on the configured port.
- If a task fails with an ImportError for missing modules, ensure the Worker environment has required libraries installed.

Developer notes

- UI files: `master/master_ui.py`, `worker/worker_ui.py` — primary places for layout and styling changes.
- Shared styles: `assets/styles.py`.
- Use `python -m py_compile <file>` to quickly check for syntax errors during edits.

Contributing

This repository was built as an academic project and is open for improvements. If you add features, please follow the existing code style and keep UI changes consistent with the project's stylesheet.

Contact

If you need help adapting WinLink for your environment or preparing a demo for your FYP defense, open an issue or contact the project owner.

---

Generated by the WinLink FYP development process — updated README to reflect current project structure and usage.
... (truncated for brevity) ...

## Quick Overview

- Master: UI to add/connect workers, create tasks from templates or custom code, monitor task queue and worker resources (`master/master_ui.py`).
- Worker: UI to configure and start a worker service that accepts tasks from the master (`worker/worker_ui.py`).
- Core: task management, execution and network protocol live in the `core/` package.

## Features

- Create and dispatch Python tasks to worker machines
- Monitor CPU / memory / disk usage on workers
- Configure resource sharing and limits per worker
- View task logs and outputs in the UIs

## Requirements

- Python 3.8+ (3.7 may work but 3.8+ recommended)
- Packages listed in `requirements.txt` (PyQt5, psutil)

## Installation

1. Clone the repository and change to the project folder:

```powershell
git clone <repository-url>
cd WinLink-FYP
```

2. (Optional) Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running the App

- Launch the role selector (recommended):

```powershell
python main.py
```

- Or run an enhanced launcher (if present):

```powershell
python launch_enhanced.py
```

Notes:
- To run the Master UI directly: `python master/master_ui.py`
- To run the Worker UI directly: `python worker/worker_ui.py`

## Folder Structure

```
WinLink-FYP/
├── core/                    # Task manager, executor, networking
├── master/                  # Master UI
│   └── master_ui.py
├── worker/                  # Worker UI
│   └── worker_ui.py
├── assets/                  # Styles and assets
│   └── styles.py
├── main.py                  # Entry / role selector
├── launch_enhanced.py      # Optional enhanced launcher
└── requirements.txt        # Python dependencies
```

## Usage Basics

Master:
- Connect workers by entering their IP and port.
- Create tasks using templates or by pasting Python code.
- Submit tasks and watch the Task Queue update (progress/results).

Worker:
- Configure which resources to share and set limits.
- Start the worker service and copy the displayed IP:PORT to the Master.

## Development & Packaging

- To package the app, `pyinstaller` can be used (optional dependency in `requirements.txt`).

Example:

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name "WinLink" main.py
```

## Troubleshooting

- If workers do not connect, check Windows Firewall or antivirus blocking sockets.
- Ensure both machines are on the same LAN and ports are reachable.
- For task JSON errors, verify the JSON structure in the task data field.

## Contributing

- This project was developed as an FYP. Contributions are welcome — open an issue or PR.