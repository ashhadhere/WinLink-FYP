import sys, os, json, threading, time
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QHeaderView, QSplitter

# Fix module path for core & assets
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

# Now import modules
from assets.styles import STYLE_SHEET
from core.task_manager import TaskManager, TASK_TEMPLATES, TaskStatus, TaskType
from core.network import MasterNetwork, MessageType

class MasterUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Master PC (Enhanced)")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)

        # Core
        self.task_manager = TaskManager()
        self.network = MasterNetwork()
        self.worker_resources = {}
        self.worker_resources_lock = threading.Lock()
        self.monitoring_active = True

        self.network.register_handler(MessageType.PROGRESS_UPDATE, self.handle_progress_update)
        self.network.register_handler(MessageType.TASK_RESULT, self.handle_task_result)
        self.network.register_handler(MessageType.RESOURCE_DATA, self.handle_resource_data)
        self.network.register_handler(MessageType.READY, self.handle_worker_ready)
        self.network.register_handler(MessageType.ERROR, self.handle_worker_error)
        self.network.start()

        # UI
        self.setup_ui()
        self.start_monitoring_thread()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Use splitter for responsive layout
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        left = self.create_worker_panel()
        right = self.create_task_panel()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])  # Initial sizes
        main_layout.addWidget(splitter)

    def create_worker_panel(self):
        panel = QtWidgets.QFrame()
        panel.setProperty("glass", True)
        lay = QtWidgets.QVBoxLayout(panel)
        lay.setSpacing(12)

        hdr = QtWidgets.QLabel("🖥️ Worker Management", panel)
        hdr.setObjectName("headerLabel")
        hdr.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(hdr)

        # Add Worker
        grp = QtWidgets.QGroupBox("Add Worker", panel)
        g_l = QtWidgets.QVBoxLayout(grp)
        self.ip_input = QtWidgets.QLineEdit(); self.ip_input.setPlaceholderText("IP")
        self.port_input = QtWidgets.QLineEdit(); self.port_input.setPlaceholderText("Port")
        self.port_input.setValidator(QtGui.QIntValidator(1,65535))
        self.connect_btn = QtWidgets.QPushButton("Connect"); self.connect_btn.setObjectName("startBtn")
        self.connect_btn.clicked.connect(self.connect_to_worker)
        for w in (self.ip_input, self.port_input, self.connect_btn):
            g_l.addWidget(w)
        lay.addWidget(grp)

        # Connected Workers
        wgrp = QtWidgets.QGroupBox("Connected Workers", panel)
        w_l = QtWidgets.QVBoxLayout(wgrp)
        self.workers_list = QtWidgets.QListWidget()
        self.disconnect_btn = QtWidgets.QPushButton("Disconnect"); self.disconnect_btn.setObjectName("stopBtn")
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.clicked.connect(self.disconnect_selected_worker)
        self.refresh_workers_btn = QtWidgets.QPushButton("Refresh"); 
        self.refresh_workers_btn.clicked.connect(self.refresh_workers)
        w_l.addWidget(self.workers_list)
        btn_h = QtWidgets.QHBoxLayout()
        btn_h.addWidget(self.disconnect_btn); btn_h.addWidget(self.refresh_workers_btn)
        w_l.addLayout(btn_h)
        lay.addWidget(wgrp)

        # Worker Resources Display - Enhanced with better styling
        rgrp = QtWidgets.QGroupBox("Live Worker Resources", panel)
        r_l = QtWidgets.QVBoxLayout(rgrp)
        self.resource_display = QtWidgets.QTextEdit()
        self.resource_display.setReadOnly(True)
        self.resource_display.setMinimumHeight(150)
        # Make font larger and more readable
        font = self.resource_display.font()
        font.setPointSize(10)  # Increase font size
        font.setFamily("Consolas")  # Use monospace font for better alignment
        self.resource_display.setFont(font)
        # Add styling for better readability
        self.resource_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 40, 0.6);
                color: #ffffff;
                border: 1px solid rgba(100, 255, 160, 0.3);
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
                line-height: 1.4;
            }
        """)
        self.resource_display.setPlainText("🔄 Waiting for worker resources...\n\nConnect workers and data will appear here automatically.")
        r_l.addWidget(self.resource_display)
        lay.addWidget(rgrp)
        
        # Add refresh button for manual resource update
        refresh_res_btn = QtWidgets.QPushButton("🔄 Refresh Resources")
        refresh_res_btn.clicked.connect(self.refresh_all_worker_resources)
        r_l.addWidget(refresh_res_btn)

        self.workers_list.itemSelectionChanged.connect(self.on_worker_selection_changed)
        return panel

    def create_task_panel(self):
        panel = QtWidgets.QFrame()
        panel.setProperty("glass", True)
        lay = QtWidgets.QVBoxLayout(panel)
        lay.setSpacing(12)

        hdr = QtWidgets.QLabel("📋 Task Management", panel)
        hdr.setObjectName("headerLabel"); hdr.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(hdr)

        # Create Task
        grp = QtWidgets.QGroupBox("Create Task", panel)
        g_l = QtWidgets.QVBoxLayout(grp)
        # Add Task Type dropdown first
        self.task_type_combo = QtWidgets.QComboBox()
        self.task_type_combo.addItems([t.name for t in TaskType])
        self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)
        g_l.addWidget(QtWidgets.QLabel("Task Type:"))
        g_l.addWidget(self.task_type_combo)
        
        self.template_combo = QtWidgets.QComboBox()
        g_l.addWidget(QtWidgets.QLabel("Template:"))
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        g_l.addWidget(self.template_combo)
        self.task_description = QtWidgets.QLabel(); self.task_description.setWordWrap(True)
        g_l.addWidget(self.task_description)
        self.task_code_edit = QtWidgets.QTextEdit(); self.task_code_edit.setMaximumHeight(120)
        g_l.addWidget(self.task_code_edit)
        self.task_data_edit = QtWidgets.QTextEdit(); self.task_data_edit.setMaximumHeight(80)
        g_l.addWidget(self.task_data_edit)
        self.submit_task_btn = QtWidgets.QPushButton("Submit Task"); self.submit_task_btn.setObjectName("startBtn")
        self.submit_task_btn.clicked.connect(self.submit_task)
        g_l.addWidget(self.submit_task_btn)
        lay.addWidget(grp)
        
        # Initialize templates after all widgets are created
        self.on_task_type_changed()

        # Task Queue
        tgrp = QtWidgets.QGroupBox("Task Queue", panel)
        t_l = QtWidgets.QVBoxLayout(tgrp)
        self.tasks_table = QtWidgets.QTableWidget(0,7)
        self.tasks_table.setHorizontalHeaderLabels(["ID","Type","Status","Worker","Progress","Result","Output"])
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.setColumnWidth(0, 70)   # ID column
        self.tasks_table.setColumnWidth(1, 90)   # Type column
        self.tasks_table.setColumnWidth(2, 80)   # Status column
        self.tasks_table.setColumnWidth(3, 120)  # Worker column
        self.tasks_table.setColumnWidth(4, 70)   # Progress column
        self.tasks_table.setColumnWidth(5, 180)  # Result column
        self.tasks_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)  # Output column stretches
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tasks_table.setWordWrap(True)  # Enable word wrap
        self.tasks_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        t_l.addWidget(self.tasks_table)
        clear_btn = QtWidgets.QPushButton("Clear Completed"); clear_btn.setObjectName("stopBtn")
        clear_btn.clicked.connect(self.clear_completed_tasks)
        t_l.addWidget(clear_btn, alignment=QtCore.Qt.AlignRight)
        lay.addWidget(tgrp)

        return panel

    def start_monitoring_thread(self):
        def monitor():
            while self.monitoring_active:
                workers = self.network.get_connected_workers()
                if workers:
                    for worker_id in workers.keys():
                        self.network.request_resources_from_worker(worker_id)
                time.sleep(2)  # Update every 2 seconds for more real-time feel
        threading.Thread(target=monitor, daemon=True).start()

    # ─── Event Handlers ───

    def on_worker_selection_changed(self):
        self.disconnect_btn.setEnabled(bool(self.workers_list.selectedItems()))

    def connect_to_worker(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        if not ip or not port:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Enter both IP and Port")
            return
        worker_id = f"{ip}:{port}"
        connected = self.network.connect_to_worker(worker_id, ip, int(port))
        if not connected:
            QtWidgets.QMessageBox.critical(self, "Connection Failed", f"Could not connect to {worker_id}")
        else:
            QtWidgets.QMessageBox.information(self, "Connected", f"Connected to {worker_id}")
            # Request resources immediately after connection
            QtCore.QTimer.singleShot(500, lambda: self.network.request_resources_from_worker(worker_id))
        self.refresh_workers_async()

    def refresh_workers(self):
        self.workers_list.clear()
        for worker_id, info in self.network.get_connected_workers().items():
            entry = f"{info['ip']}:{info['port']}"
            self.workers_list.addItem(entry)

    def disconnect_selected_worker(self):
        sel = self.workers_list.currentItem()
        if sel:
            # Get IP:Port from list item
            ip_port = sel.text()
            # Find the worker_id that matches this IP:Port
            worker_id = None
            for wid, info in self.network.get_connected_workers().items():
                if f"{info['ip']}:{info['port']}" == ip_port:
                    worker_id = wid
                    break
            if worker_id:
                self.network.disconnect_worker(worker_id)
                # Remove from resources
                with self.worker_resources_lock:
                    self.worker_resources.pop(worker_id, None)
            self.refresh_workers_async()

    def on_task_type_changed(self):
        """Update template dropdown based on selected task type"""
        selected_type_name = self.task_type_combo.currentText()
        try:
            selected_type = TaskType[selected_type_name]
        except KeyError:
            return
        
        # Filter templates by task type
        self.template_combo.clear()
        for template_key, template_data in TASK_TEMPLATES.items():
            if template_data.get("type") == selected_type:
                self.template_combo.addItem(template_key)
        
        # If no templates found, add a custom option
        if self.template_combo.count() == 0:
            self.template_combo.addItem("Custom")
        
        # Trigger template change to load first template
        if self.template_combo.count() > 0:
            self.on_template_changed(self.template_combo.currentText())
    
    def on_template_changed(self, name):
        if not name or name == "Custom":
            self.task_description.setText("Enter custom task code")
            self.task_code_edit.clear()
            self.task_data_edit.setPlainText("{}")
            return
            
        desc = TASK_TEMPLATES.get(name, {}).get("description", "")
        code = TASK_TEMPLATES.get(name, {}).get("code", "")
        sample_data = TASK_TEMPLATES.get(name, {}).get("sample_data")
        self.task_description.setText(desc)
        self.task_code_edit.setPlainText(code)
        if sample_data is not None:
            self.task_data_edit.setPlainText(json.dumps(sample_data, indent=2))
        else:
            self.task_data_edit.setPlainText("{}")

    def submit_task(self):
        code = self.task_code_edit.toPlainText()
        if not code.strip():
            QtWidgets.QMessageBox.warning(self, "Missing Code", "Task code cannot be empty.")
            return
        
        try:
            data = json.loads(self.task_data_edit.toPlainText() or "{}")
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.critical(self, "Invalid JSON", "Task data must be valid JSON.")
            return

        try:
            selected_type = TaskType[self.task_type_combo.currentText()]
        except KeyError:
            QtWidgets.QMessageBox.critical(self, "Invalid Task Type", "Selected task type is not valid.")
            return

        if not self.network.get_connected_workers():
            QtWidgets.QMessageBox.warning(self, "No Workers", "Connect at least one worker before submitting tasks.")
            return

        task_id = self.task_manager.create_task(selected_type, code, data)
        if not self.dispatch_task_to_worker(task_id, code, data):
            QtWidgets.QMessageBox.critical(self, "Dispatch Failed", "Failed to dispatch task to any worker.")
        self.refresh_task_table_async()

    def dispatch_task_to_worker(self, task_id: str, code: str, data: dict) -> bool:
        workers = self.network.get_connected_workers()
        if not workers:
            return False

        target_worker = self._select_worker(workers)
        if not target_worker:
            return False

        payload = {
            'task_id': task_id,
            'code': code,
            'data': data
        }
        sent = self.network.send_task_to_worker(target_worker, payload)
        if sent:
            self.task_manager.assign_task_to_worker(task_id, target_worker)
        return sent

    def _select_worker(self, workers: dict) -> str:
        resources = self._get_worker_resources_snapshot()
        best_worker = None
        best_score = -1
        for worker_id in workers.keys():
            stats = resources.get(worker_id, {})
            score = stats.get('memory_available_mb', 0) or 0
            if score > best_score:
                best_score = score
                best_worker = worker_id
        if not best_worker and workers:
            best_worker = next(iter(workers.keys()))
        return best_worker

    def refresh_task_table(self):
        tasks = sorted(self.task_manager.get_all_tasks(), key=lambda t: t.created_at, reverse=True)
        self.tasks_table.setRowCount(len(tasks))
        for row, t in enumerate(tasks):
            # ID column
            id_item = QtWidgets.QTableWidgetItem(t.id[:8])
            self.tasks_table.setItem(row, 0, id_item)
            
            # Type column
            type_item = QtWidgets.QTableWidgetItem(t.type.name)
            self.tasks_table.setItem(row, 1, type_item)
            
            # Status column
            status_item = QtWidgets.QTableWidgetItem(t.status.name)
            self.tasks_table.setItem(row, 2, status_item)
            
            # Worker column - show only IP
            worker_text = ""
            if t.worker_id:
                worker_text = t.worker_id.split(":")[0] if ":" in t.worker_id else t.worker_id
            worker_item = QtWidgets.QTableWidgetItem(worker_text)
            self.tasks_table.setItem(row, 3, worker_item)
            
            # Progress column
            progress_item = QtWidgets.QTableWidgetItem(f"{t.progress}%")
            self.tasks_table.setItem(row, 4, progress_item)
            
            # Result column - show formatted summary (one line, readable)
            result_text = ""
            if t.result is not None:
                if isinstance(t.result, dict):
                    # Create a readable summary
                    result_parts = []
                    for key, val in list(t.result.items())[:3]:  # Show first 3 items
                        if isinstance(val, (int, float)):
                            result_parts.append(f"{key}: {val}")
                        elif isinstance(val, str) and len(val) < 30:
                            result_parts.append(f"{key}: {val}")
                        else:
                            result_parts.append(f"{key}: ...")
                    result_text = ", ".join(result_parts)
                    if len(t.result) > 3:
                        result_text += f" (+{len(t.result)-3} more)"
                elif isinstance(t.result, (list, tuple)):
                    if len(t.result) <= 3:
                        result_text = str(t.result)
                    else:
                        result_text = str(list(t.result)[:3]) + f" ... (+{len(t.result)-3} more)"
                else:
                    result_str = str(t.result)
                    result_text = result_str[:100] + ("..." if len(result_str) > 100 else "")
            elif t.error:
                result_text = f"Error: {t.error[:80]}"
            else:
                result_text = "Pending..."
            result_item = QtWidgets.QTableWidgetItem(result_text)
            result_item.setToolTip(result_text)  # Show full text on hover
            self.tasks_table.setItem(row, 5, result_item)
            
            # Output column - show full formatted output with proper wrapping
            output_text = ""
            if hasattr(t, 'output') and t.output:
                output_text = str(t.output)
            elif t.error:
                output_text = f"ERROR:\n{t.error}"
            elif t.result is not None:
                # Format result nicely for output
                if isinstance(t.result, dict):
                    output_lines = []
                    for key, val in t.result.items():
                        if isinstance(val, (dict, list)):
                            output_lines.append(f"{key}: {json.dumps(val, indent=2)}")
                        else:
                            output_lines.append(f"{key}: {val}")
                    output_text = "\n".join(output_lines)
                elif isinstance(t.result, (list, tuple)):
                    output_text = json.dumps(list(t.result) if isinstance(t.result, tuple) else t.result, indent=2)
                else:
                    output_text = str(t.result)
            else:
                output_text = "No output yet"
            
            output_item = QtWidgets.QTableWidgetItem(output_text)
            output_item.setToolTip(output_text)  # Show full text on hover
            # Enable word wrap for output column
            output_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.tasks_table.setItem(row, 6, output_item)
            
            # Set row height to accommodate wrapped text
            self.tasks_table.setRowHeight(row, max(30, len(output_text.split('\n')) * 20))

    def refresh_task_table_async(self):
        QtCore.QTimer.singleShot(0, self.refresh_task_table)

    def handle_progress_update(self, worker_id, data):
        task_id = data.get("task_id")
        progress = data.get("progress", 0)
        self.task_manager.update_task_progress(task_id, progress)
        self.refresh_task_table_async()

    def handle_task_result(self, worker_id, data):
        task_id = data.get("task_id")
        result_payload = data.get("result", {})
        
        # Store full output including stdout/stderr
        task = self.task_manager.get_task(task_id)
        if task:
            output_parts = []
            if result_payload.get("stdout"):
                output_parts.append(f"STDOUT:\n{result_payload['stdout']}")
            if result_payload.get("stderr"):
                output_parts.append(f"STDERR:\n{result_payload['stderr']}")
            if result_payload.get("result") is not None:
                output_parts.append(f"RESULT:\n{json.dumps(result_payload['result'], indent=2) if isinstance(result_payload['result'], dict) else str(result_payload['result'])}")
            
            task.output = "\n\n".join(output_parts) if output_parts else None
        
        self.task_manager.update_task(task_id, worker_id, result_payload)
        self.refresh_task_table_async()

    def handle_resource_data(self, worker_id, data):
        with self.worker_resources_lock:
            self.worker_resources[worker_id] = data
        
        def format_resources():
            snapshot = self._get_worker_resources_snapshot()
            if not snapshot:
                return "🔄 Waiting for worker resources...\n\nConnect workers and data will appear here automatically."
            
            lines = []
            for wid, stats in snapshot.items():
                cpu = stats.get("cpu_percent", 0.0)
                mem_avail = stats.get("memory_available_mb", 0.0)
                mem_percent = stats.get("memory_percent", 0.0)
                mem_total = stats.get("memory_total_mb", 0.0)
                mem_used = mem_total - mem_avail if mem_total > 0 else 0
                disk = stats.get("disk_percent", 0.0)
                disk_free = stats.get("disk_free_gb", 0.0)
                battery = stats.get("battery_percent")
                plugged = stats.get("battery_plugged")
                
                # Extract IP from worker_id (format: "ip:port")
                worker_ip = wid.split(":")[0] if ":" in wid else wid
                
                # Create visual indicators for resource usage
                def get_indicator(percent):
                    if percent < 50:
                        return "🟢"  # Green - Good
                    elif percent < 75:
                        return "🟡"  # Yellow - Moderate
                    else:
                        return "🔴"  # Red - High
                
                def get_bar(percent, width=20):
                    """Create a visual bar for percentage"""
                    filled = int((percent / 100) * width)
                    bar = "█" * filled + "░" * (width - filled)
                    return bar
                
                line = "╔══════════════════════════════════════════════╗\n"
                line += f"║  🖥️  WORKER: {worker_ip:<30} ║\n"
                line += "╚══════════════════════════════════════════════╝\n\n"
                
                # CPU with visual bar
                cpu_indicator = get_indicator(cpu)
                line += f"{cpu_indicator} CPU USAGE: {cpu:>5.1f}%\n"
                line += f"   {get_bar(cpu)} \n\n"
                
                # Memory with visual bar
                mem_indicator = get_indicator(mem_percent)
                mem_total_gb = mem_total / 1024
                mem_used_gb = mem_used / 1024
                mem_avail_gb = mem_avail / 1024
                line += f"{mem_indicator} MEMORY USAGE: {mem_percent:>5.1f}%\n"
                line += f"   {get_bar(mem_percent)} \n"
                line += f"   📊 Total:     {mem_total_gb:>6.2f} GB\n"
                line += f"   📈 Used:      {mem_used_gb:>6.2f} GB\n"
                line += f"   📉 Available: {mem_avail_gb:>6.2f} GB\n\n"
                
                # Disk with visual bar
                disk_indicator = get_indicator(disk)
                line += f"{disk_indicator} DISK USAGE: {disk:>5.1f}%\n"
                line += f"   {get_bar(disk)} \n"
                line += f"   💾 Free Space: {disk_free:>6.1f} GB\n\n"
                
                # Battery status
                if battery is not None:
                    icon = "🔌" if plugged else "🔋"
                    status = "Charging" if plugged else "Discharging"
                    bat_indicator = get_indicator(100 - battery if not plugged else 0)
                    line += f"{icon} BATTERY: {battery:>5.0f}% ({status})\n"
                    if not plugged:
                        line += f"   {get_bar(battery)} \n"
                else:
                    line += "⚡ POWER: AC (No Battery)\n"
                
                lines.append(line)
            
            header = f"🔄 LIVE RESOURCES ({len(snapshot)} Worker{'s' if len(snapshot) > 1 else ''})\n"
            header += f"Last Updated: {time.strftime('%H:%M:%S')}\n"
            header += "═" * 48 + "\n\n"
            
            return header + "\n".join(lines) if lines else "No worker resources available."
        
        QtCore.QTimer.singleShot(0, lambda: self.resource_display.setPlainText(format_resources()))
        self.refresh_workers_async()

    def handle_worker_ready(self, worker_id, data):
        self.network.request_resources_from_worker(worker_id)
        self.refresh_workers_async()

    def handle_worker_error(self, worker_id, data):
        task_id = data.get("task_id")
        error = data.get("error", "Unknown error")
        if task_id:
            self.task_manager.update_task(task_id, worker_id, {
                "success": False,
                "result": None,
                "error": error
            })
            self.refresh_task_table_async()
        QtCore.QTimer.singleShot(
            0,
            lambda: QtWidgets.QMessageBox.critical(
                self,
                "Worker Error",
                f"Worker {worker_id} reported an error:\n{error}"
            )
        )

    def clear_completed_tasks(self):
        self.task_manager.clear_tasks(status=TaskStatus.COMPLETED)
        self.refresh_task_table()

    def refresh_workers_async(self):
        QtCore.QTimer.singleShot(0, self.refresh_workers)

    def refresh_all_worker_resources(self):
        """Manually request resources from all connected workers"""
        workers = self.network.get_connected_workers()
        if not workers:
            QtWidgets.QMessageBox.information(self, "No Workers", "No workers are currently connected.")
            return
        
        for worker_id in workers.keys():
            self.network.request_resources_from_worker(worker_id)
        
        # Show confirmation
        QtCore.QTimer.singleShot(0, lambda: self.resource_display.setPlainText(
            f"🔄 Refreshing resources from {len(workers)} worker(s)...\n\nPlease wait..."
        ))

    def _get_worker_resources_snapshot(self):
        with self.worker_resources_lock:
            return {wid: data.copy() for wid, data in self.worker_resources.items()}

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Handle window close event - cleanup resources"""
        try:
            self.monitoring_active = False
            # Give monitoring thread a moment to stop
            time.sleep(0.1)
            self.network.stop()
        except Exception as ex:
            print(f"Error during cleanup: {ex}")
        finally:
            super().closeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MasterUI()
    win.show()
    sys.exit(app.exec_())
