# worker/worker_ui_enhanced.py

import sys, os, socket, threading, psutil, time, json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QTextEdit, QGroupBox, QCheckBox, QSpinBox,
    QFormLayout, QLineEdit, QGraphicsDropShadowEffect, QMessageBox,
    QFileDialog, QSizePolicy, QSplitter
)
from PyQt5.QtGui import QColor, QIntValidator, QTextCursor
from PyQt5.QtCore import Qt, QTimer

# ──────────────────────────────────────────────────────────────────────────────
# Ensure that `core/` and `assets/` sit on sys.path
ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ──────────────────────────────────────────────────────────────────────────────

from core.task_executor import TaskExecutor
from core.network import WorkerNetwork, MessageType, NetworkMessage
from assets.styles import STYLE_SHEET


class WorkerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Worker PC (Enhanced)")
        self.setMinimumSize(800, 600)

        # Core
        self.network = WorkerNetwork()
        self.task_executor = TaskExecutor()
        self.current_tasks = {}
        self.tasks_lock = threading.Lock()
        self.monitoring_active = True
        self.last_output_text = "No task output yet."

        # Network handlers
        self.network.register_handler(MessageType.TASK_REQUEST, self.handle_task_request)
        self.network.register_handler(MessageType.RESOURCE_REQUEST, self.handle_resource_request)
        self.network.register_handler(MessageType.HEARTBEAT, self.handle_heartbeat)

        # Build UI
        self.setup_ui()
        self.update_ip()
        self.start_monitoring_thread()

    def handle_resource_request(self, data):
        try:
            resource_data = self.task_executor.get_system_resources()
            self.network.send_resource_data(resource_data)
        except Exception as e:
            self.log(f"Error in handle_resource_request: {e}")

    def handle_heartbeat(self, data):
        msg = NetworkMessage(MessageType.HEARTBEAT_RESPONSE, {
            "timestamp": time.time()
        })
        self.network.send_message_to_master(msg)

    def setup_ui(self):
        self.setStyleSheet(STYLE_SHEET)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Header
        title = QLabel("WinLink – Worker PC (Enhanced)")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Responsive splitter for panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.addWidget(self.create_connection_panel())
        splitter.addWidget(self.create_task_panel())
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter, 1)

    def create_connection_panel(self):
        panel = QFrame()
        panel.setProperty("glass", True)
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)

        # — Connection Settings —
        conn_gb = QGroupBox("Connection Settings")
        conn_layout = QVBoxLayout(conn_gb)
        conn_layout.setContentsMargins(12, 12, 12, 12)
        conn_layout.setSpacing(8)

        self.ip_label = QLabel("IP Address: –")
        self.ip_label.setObjectName("ipLabel")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port (e.g. 5001)")
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setObjectName("portInput")

        conn_layout.addWidget(self.ip_label)
        conn_layout.addWidget(self.port_input)
        layout.addWidget(conn_gb)

        # — Share Resources —
        share_gb = QGroupBox("Share Resources")
        share_gb.setMinimumHeight(200)
        share_gb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        share_layout = QVBoxLayout(share_gb)
        share_layout.setContentsMargins(12, 12, 12, 12)
        share_layout.setSpacing(8)

        # push items up
        share_layout.addStretch()

        for text, default in [
            ("CPU Processing", True),
            ("Memory (RAM)", True),
            ("Storage Access", False)
        ]:
            cb = QCheckBox(text)
            cb.setChecked(default)
            share_layout.addWidget(cb)

        # Limits
        limits = QFormLayout()
        limits.setContentsMargins(0, 8, 0, 0)
        limits.setHorizontalSpacing(10)
        limits.setVerticalSpacing(6)

        self.cpu_limit = QSpinBox()
        self.cpu_limit.setRange(10, 100)
        self.cpu_limit.setValue(80)
        self.cpu_limit.setSuffix("%")
        self.cpu_limit.setFixedHeight(20)  # Increased height
        self.cpu_limit.setMinimumWidth(120)
        self.cpu_limit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.mem_limit = QSpinBox()
        self.mem_limit.setRange(256, 8192)
        self.mem_limit.setValue(512)
        self.mem_limit.setSuffix(" MB")
        self.mem_limit.setFixedHeight(20)  # Increased height
        self.mem_limit.setMinimumWidth(120)
        self.mem_limit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        limits.addRow("Max CPU:", self.cpu_limit)
        limits.addRow("Max Memory:", self.mem_limit)

        share_layout.addLayout(limits)
        share_layout.addStretch()
        layout.addWidget(share_gb)

        # — Connection Status —
        status_gb = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_gb)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.setSpacing(8)

        self.status_label = QLabel("Status: 🔴 Idle")
        self.status_label.setObjectName("infoLabel")

        self.conn_str = QLineEdit("N/A")
        self.conn_str.setReadOnly(True)
        self.conn_str.setStyleSheet("background: transparent; border: none; color: white;")

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setObjectName("copyBtn")
        self.copy_btn.setFixedSize(60, 30)
        self.copy_btn.clicked.connect(self.on_copy_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(self.conn_str)
        hbox.addWidget(self.copy_btn)

        status_layout.addWidget(self.status_label)
        status_layout.addLayout(hbox)
        layout.addWidget(status_gb)

        # — Start / Stop Buttons —
        self.start_btn = QPushButton("Start Worker")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_worker)

        self.stop_btn = QPushButton("Stop Worker")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.clicked.connect(self.stop_worker)
        self.stop_btn.setEnabled(False)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        layout.addStretch()
        self.apply_shadow(panel)
        return panel

    def create_task_panel(self):
        panel = QFrame()
        panel.setProperty("glass", True)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Current Tasks
        tasks_gb = QGroupBox("Current Tasks")
        v = QVBoxLayout(tasks_gb)
        v.setContentsMargins(8, 8, 8, 8)
        self.tasks_display = QTextEdit()
        self.tasks_display.setObjectName("tasksDisplay")
        self.tasks_display.setReadOnly(True)
        self.tasks_display.setPlainText("No active tasks.")
        self.tasks_display.setMinimumHeight(70)
        self.tasks_display.setMaximumHeight(100)
        v.addWidget(self.tasks_display)
        layout.addWidget(tasks_gb)
        
        # Task Output Display
        output_gb = QGroupBox("Task Output")
        ov = QVBoxLayout(output_gb)
        ov.setContentsMargins(8, 8, 8, 8)
        self.task_output_display = QTextEdit()
        self.task_output_display.setObjectName("tasksDisplay")
        self.task_output_display.setReadOnly(True)
        self.task_output_display.setPlainText("No task output yet.")
        self.task_output_display.setMinimumHeight(70)
        self.task_output_display.setMaximumHeight(100)
        ov.addWidget(self.task_output_display)
        layout.addWidget(output_gb)

        # System Resources
        res_gb = QGroupBox("System Resources")
        rv = QVBoxLayout(res_gb)
        rv.setContentsMargins(8, 8, 8, 8)

        # Build and stash bar layouts
        self.cpu_bar_layout  = self._make_bar("CPU Usage:",    "#00f5a0")
        self.mem_bar_layout  = self._make_bar("Memory Usage:", "#667eea")
        self.disk_bar_layout = self._make_bar("Disk Usage:",   "#ffb74d")

        rv.addLayout(self.cpu_bar_layout)
        rv.addLayout(self.mem_bar_layout)
        rv.addLayout(self.disk_bar_layout)

        # Extract widgets
        self.cpu_bar    = self.cpu_bar_layout .itemAt(1).widget()
        self.cpu_label  = self.cpu_bar_layout .itemAt(2).widget()
        self.mem_bar    = self.mem_bar_layout .itemAt(1).widget()
        self.mem_label  = self.mem_bar_layout .itemAt(2).widget()
        self.disk_bar   = self.disk_bar_layout.itemAt(1).widget()
        self.disk_label = self.disk_bar_layout.itemAt(2).widget()

        self.res_details = QTextEdit()
        self.res_details.setReadOnly(True)
        self.res_details.setMinimumHeight(60)
        self.res_details.setMaximumHeight(100)
        rv.addWidget(self.res_details)

        layout.addWidget(res_gb)

        # Task Log - Make it visible and properly sized (MUST BE VISIBLE)
        log_gb = QGroupBox("Task Execution Log")
        lv = QVBoxLayout(log_gb)
        lv.setContentsMargins(8, 8, 8, 8)
        self.task_log = QTextEdit()
        self.task_log.setReadOnly(True)
        self.task_log.setMinimumHeight(100)
        self.task_log.setMaximumHeight(180)
        self.task_log.setPlainText("Task execution log will appear here...")
        btns = QHBoxLayout()
        c = QPushButton("Clear");  c.clicked.connect(self.task_log.clear)
        e = QPushButton("Export"); e.clicked.connect(self.export_log)
        btns.addWidget(c); btns.addWidget(e); btns.addStretch()
        lv.addWidget(self.task_log)
        lv.addLayout(btns)
        layout.addWidget(log_gb)

        self.apply_shadow(panel)
        return panel

    def _make_bar(self, text, color):
        h = QHBoxLayout()
        lbl = QLabel(text)
        lbl.setMinimumWidth(110)
        lbl.setObjectName("infoLabel")

        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setMaximumHeight(18)
        bar.setStyleSheet(f"QProgressBar::chunk {{ background: {color}; border-radius: 9px; }}")

        val = QLabel("0%")
        val.setMinimumWidth(40)
        val.setAlignment(Qt.AlignCenter)

        h.addWidget(lbl)
        h.addWidget(bar)
        h.addWidget(val)
        return h

    def apply_shadow(self, w):
        shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=6, color=QColor(0,0,0,150))
        w.setGraphicsEffect(shadow)

    def update_ip(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
            self.ip_label.setText(f"IP Address: {ip}")
        except:
            self.ip_label.setText("IP Address: Unavailable")

    def start_worker(self):
        port = self.port_input.text().strip()
        if not port:
            QMessageBox.warning(self, "Missing Port", "Enter port to start.")
            return

        if self.network.start_server(int(port)):
            self.status_label.setText("Status: 🟢 Running")
            self.conn_str.setText(f"{self.network.ip}:{port}")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.log("Worker started")
        else:
            QMessageBox.critical(self, "Error", "Failed to start.")

    def stop_worker(self):
        self.network.stop()
        self.status_label.setText("Status: 🔴 Idle")
        self.conn_str.setText("N/A")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("Worker stopped")

    def on_copy_clicked(self):
        QApplication.clipboard().setText(self.conn_str.text())
        prev = self.status_label.text()
        self.status_label.setText("✅ Copied!")
        QTimer.singleShot(2000, lambda: self.status_label.setText(prev))

    def handle_task_request(self, data):
        task_id = data.get("task_id")
        code = data.get("code", "")
        payload = data.get("data", {})

        if not task_id or not code:
            self.log("Received malformed task request.")
            self._send_error_to_master(task_id or "unknown", "Invalid task payload received by worker.")
            return

        self.log(f"📥 Received task: {task_id}")
        self.log(f"   Code length: {len(code)} chars, Data keys: {list(payload.keys()) if payload else 'none'}")
        
        # Immediately show the task in the UI - ensure it's visible right away
        with self.tasks_lock:
            self.current_tasks[task_id] = {
                "status": "pending",
                "progress": 0,
                "started_at": None,
                "memory_used_mb": 0,
                "output": None
            }
        # Schedule UI updates on the Qt main thread
        QTimer.singleShot(0, self._refresh_tasks_display)
        QTimer.singleShot(0, self._refresh_output_display)

        def run_task():
            self.log(f"▶️ Starting execution of task: {task_id}")
            self._set_task_state(task_id, status="running", progress=0, started_at=time.time())
            self.send_progress_update(task_id, 0)

            result = self.task_executor.execute_task(
                code,
                payload,
                progress_callback=lambda pct: self.send_progress_update(task_id, pct)
            )

            status = "done" if result.get("success") else "failed"
            progress_final = 100 if result.get("success") else max(0, min(99, self._get_task_progress(task_id)))
            self.send_progress_update(task_id, progress_final)

            # Build output text
            output_parts = []
            if result.get("stdout"):
                output_parts.append(f"STDOUT:\n{result['stdout']}")
            if result.get("stderr"):
                output_parts.append(f"STDERR:\n{result['stderr']}")
            if result.get("result") is not None:
                result_val = result.get("result")
                if isinstance(result_val, dict):
                    output_parts.append(f"RESULT:\n{json.dumps(result_val, indent=2)}")
                else:
                    output_parts.append(f"RESULT:\n{result_val}")
            if result.get("error"):
                output_parts.append(f"ERROR:\n{result['error']}")
            
            output_text = "\n\n".join(output_parts) if output_parts else "No output generated."
            memory_used_mb = result.get("memory_used", 0)
            
            result_payload = {
                "success": result.get("success"),
                "result": result.get("result"),
                "error": result.get("error"),
                "stdout": result.get("stdout"),
                "stderr": result.get("stderr"),
                "execution_time": result.get("execution_time"),
                "memory_used": memory_used_mb
            }
            self.network.send_task_result(task_id, result_payload)

            if result.get("success"):
                exec_time = result.get("execution_time", 0)
                self.log(f"✅ Task {task_id} completed successfully!")
                self.log(f"   Execution time: {exec_time:.2f}s")
                self.log(f"   Memory used: {memory_used_mb:.1f}MB")
                if result.get("stdout"):
                    self.log(f"   Output: {result['stdout'][:100]}...")
            else:
                error_msg = result.get('error', 'Unknown error')
                self.log(f"❌ Task {task_id} failed!")
                self.log(f"   Error: {error_msg}")

            self._set_task_state(
                task_id, 
                status=status, 
                progress=progress_final, 
                completed_at=time.time(),
                memory_used_mb=memory_used_mb,
                output=output_text
            )
            # Schedule cleanup on the Qt main thread
            QTimer.singleShot(0, lambda: self._schedule_task_cleanup(task_id))

        threading.Thread(target=run_task, daemon=True).start()

    def send_progress_update(self, task_id: str, progress: int):
        clamped = max(0, min(100, int(progress)))
        self._set_task_state(task_id, progress=clamped)
        msg = NetworkMessage(MessageType.PROGRESS_UPDATE, {
            'task_id': task_id,
            'progress': clamped
        })
        self.network.send_message_to_master(msg)

    def log(self, msg):
        now = time.strftime("%H:%M:%S")

        def append():
            lines = self.task_log.toPlainText().splitlines()[-99:]
            lines.append(f"[{now}] {msg}")
            self.task_log.setPlainText("\n".join(lines))
            self.task_log.moveCursor(QTextCursor.End)

        QTimer.singleShot(0, append)

    def export_log(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save Log", f"worker_log_{int(time.time())}.txt",
                                            "Text Files (*.txt)")
        if fn:
            with open(fn, "w") as f:
                f.write(self.task_log.toPlainText())
            QMessageBox.information(self, "Exported", f"Log saved to {fn}")

    def start_monitoring_thread(self):
        def monitor():
            while self.monitoring_active:
                time.sleep(3)
                try:
                    stats = self.task_executor.get_system_resources()
                    QTimer.singleShot(0, lambda s=stats: self._update_resources(s))
                except Exception as exc:
                    self.log(f"Resource monitor error: {exc}")
        threading.Thread(target=monitor, daemon=True).start()

    def _update_resources(self, r):
        cpu = r.get('cpu_percent', 0.0)
        mem = r.get('memory_percent', 0.0)
        disk = r.get('disk_percent', 0.0)
        battery = r.get('battery_percent')
        plugged = r.get('battery_plugged')

        self.cpu_bar.setValue(int(cpu))
        self.cpu_label.setText(f"{cpu:.1f}%")
        self.mem_bar.setValue(int(mem))
        self.mem_label.setText(f"{mem:.1f}%")
        self.disk_bar.setValue(int(disk))
        self.disk_label.setText(f"{disk:.1f}%")

        battery_str = "Unavailable"
        if battery is not None:
            battery_str = f"{battery:.0f}% {'(Charging)' if plugged else ''}"

        with self.tasks_lock:
            active_tasks = len([t for t in self.current_tasks.values() if t.get('status') == 'running'])

        # Calculate RAM used by tasks
        task_memory_mb = 0
        with self.tasks_lock:
            for task_meta in self.current_tasks.values():
                task_memory_mb += task_meta.get('memory_used_mb', 0)
        
        details = (
            f"CPU Cores: {psutil.cpu_count()}\n"
            f"Total Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB\n"
            f"Available Memory: {r.get('memory_available_mb', 0):.0f} MB\n"
            f"Memory Used by Tasks: {task_memory_mb:.1f} MB\n"
            f"Free Disk Space: {r.get('disk_free_gb', 0):.1f} GB\n"
            f"Battery: {battery_str}\n"
            f"Active Tasks: {active_tasks}"
        )
        self.res_details.setPlainText(details)


    def _set_task_state(self, task_id: str, **updates):
        with self.tasks_lock:
            state = self.current_tasks.setdefault(task_id, {
                "status": "pending", 
                "progress": 0,
                "memory_used_mb": 0,
                "output": None
            })
            state.update(updates)
            if updates.get("output"):
                self.last_output_text = updates["output"]
        # Schedule UI updates on the Qt main thread
        QTimer.singleShot(0, self._refresh_tasks_display)
        QTimer.singleShot(0, self._refresh_output_display)

    def _refresh_tasks_display(self):
        with self.tasks_lock:
            if not self.current_tasks:
                display = "No active tasks."
            else:
                lines = []
                for tid, meta in sorted(self.current_tasks.items(), key=lambda x: x[1].get("started_at") or 0, reverse=True):
                    progress = meta.get("progress", 0)
                    status = meta.get("status", "pending").title()
                    mem_used = meta.get("memory_used_mb", 0)
                    started_at = meta.get("started_at")
                    
                    # Format time info
                    time_info = ""
                    if started_at:
                        elapsed = time.time() - started_at
                        time_info = f" | Elapsed: {elapsed:.1f}s"
                    
                    mem_str = f" | RAM: {mem_used:.1f}MB" if mem_used > 0 else ""
                    status_icon = "▶️" if status == "Running" else "✅" if status == "Done" else "❌" if status == "Failed" else "⏳"
                    lines.append(f"{status_icon} Task {tid[:8]}\n   Status: {status} | Progress: {progress}%{mem_str}{time_info}")
                display = "\n\n".join(lines)
        QTimer.singleShot(0, lambda txt=display: self.tasks_display.setPlainText(txt))
    
    def _refresh_output_display(self):
        """Display output from the most recent or active task"""
        with self.tasks_lock:
            if not self.current_tasks:
                output_text = self.last_output_text if self.last_output_text != "No task output yet." else "No task output yet.\n\nTask output will appear here when tasks are executed."
            else:
                # Find the most recent task with output
                tasks_with_output = [
                    (tid, meta) for tid, meta in self.current_tasks.items() 
                    if meta.get("output")
                ]
                if tasks_with_output:
                    # Sort by completed_at or started_at (most recent first)
                    tasks_with_output.sort(
                        key=lambda x: x[1].get("completed_at") or x[1].get("started_at") or 0,
                        reverse=True
                    )
                    latest_tid, latest_meta = tasks_with_output[0]
                    output_text = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    output_text += f"Task {latest_tid[:8]} Output:\n"
                    output_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    output_text += latest_meta.get('output', '')
                else:
                    # Show active/running tasks
                    active = [(tid, meta) for tid, meta in self.current_tasks.items() 
                             if meta.get("status") == "running"]
                    if active:
                        active_tid = active[0][0]
                        progress = active[0][1].get("progress", 0)
                        output_text = f"Task {active_tid[:8]} is running...\n"
                        output_text += f"Progress: {progress}%\n"
                        output_text += f"\n(Output will appear when task completes)"
                    else:
                        # Show pending tasks
                        pending = [(tid, meta) for tid, meta in self.current_tasks.items() 
                                  if meta.get("status") == "pending"]
                        if pending:
                            output_text = f"Task {pending[0][0][:8]} is pending...\n(Waiting to start execution)"
                        else:
                            output_text = self.last_output_text if self.last_output_text != "No task output yet." else "No task output yet."
        QTimer.singleShot(0, lambda txt=output_text: self.task_output_display.setPlainText(txt))

    def _schedule_task_cleanup(self, task_id: str, delay_ms: int = 15000):
        def cleanup():
            with self.tasks_lock:
                state = self.current_tasks.get(task_id)
                if state and state.get("status") in {"done", "failed"}:
                    self.current_tasks.pop(task_id, None)
            self._refresh_tasks_display()
        QTimer.singleShot(delay_ms, cleanup)

    def _send_error_to_master(self, task_id: str, error_message: str):
        payload = {
            "task_id": task_id,
            "error": error_message
        }
        self.network.send_message_to_master(NetworkMessage(MessageType.ERROR, payload))

    def _get_task_progress(self, task_id: str) -> int:
        with self.tasks_lock:
            return self.current_tasks.get(task_id, {}).get("progress", 0)

    def closeEvent(self, e):
        """Handle window close event - cleanup resources"""
        try:
            self.monitoring_active = False
            # Give monitoring thread a moment to stop
            import time
            time.sleep(0.1)
            self.network.stop()
        except Exception as ex:
            print(f"Error during cleanup: {ex}")
        finally:
            e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WorkerUI()
    win.show()
    sys.exit(app.exec_())
