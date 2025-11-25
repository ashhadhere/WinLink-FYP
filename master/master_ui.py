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

        # Worker Resources Display - Clean and readable
        rgrp = QtWidgets.QGroupBox("Live Worker Resources", panel)
        r_l = QtWidgets.QVBoxLayout(rgrp)
        self.resource_display = QtWidgets.QTextEdit()
        self.resource_display.setReadOnly(True)
        self.resource_display.setMinimumHeight(150)
        # Readable font size
        font = self.resource_display.font()
        font.setPointSize(9)  # Comfortable font size
        font.setFamily("Consolas")  # Monospace font for alignment
        self.resource_display.setFont(font)
        # Simple styling
        self.resource_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 40, 0.6);
                color: #e0e0e0;
                border: 1px solid rgba(100, 255, 160, 0.3);
                border-radius: 8px;
                padding: 10px;
                font-size: 9pt;
            }
        """)
        self.resource_display.setPlainText("⏳ Waiting for worker resources...\n\nConnect a worker and resources will appear here.")
        r_l.addWidget(self.resource_display)
        
        # Add refresh button
        refresh_res_btn = QtWidgets.QPushButton("🔄 Refresh Resources")
        refresh_res_btn.clicked.connect(self.refresh_all_worker_resources)
        r_l.addWidget(refresh_res_btn)
        lay.addWidget(rgrp)

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
            # Request resources immediately and repeatedly to ensure we get data
            self.resource_display.setPlainText(f"✅ Connected to {worker_id}\n\n⏳ Waiting for resource data...")
            QtCore.QTimer.singleShot(300, lambda: self.network.request_resources_from_worker(worker_id))
            QtCore.QTimer.singleShot(1000, lambda: self.network.request_resources_from_worker(worker_id))
            QtCore.QTimer.singleShot(2000, lambda: self.network.request_resources_from_worker(worker_id))
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
        """Handle incoming resource data from workers"""
        print(f"[DEBUG] ✅ Received resource data from {worker_id}:")
        print(f"[DEBUG]    CPU: {data.get('cpu_percent', 0):.1f}%")
        print(f"[DEBUG]    Memory: {data.get('memory_percent', 0):.1f}%")
        print(f"[DEBUG]    RAM Total: {data.get('memory_total_mb', 0):.0f} MB")
        print(f"[DEBUG]    RAM Available: {data.get('memory_available_mb', 0):.0f} MB")
        print(f"[DEBUG]    Disk: {data.get('disk_percent', 0):.1f}%")
        print(f"[DEBUG]    Disk Free: {data.get('disk_free_gb', 0):.1f} GB")
        print(f"[DEBUG]    Battery: {data.get('battery_percent')}% (Plugged: {data.get('battery_plugged')})")
        
        with self.worker_resources_lock:
            self.worker_resources[worker_id] = data.copy()  # Make a copy to avoid reference issues
            print(f"[DEBUG] 💾 Worker resources stored for {worker_id}")
            print(f"[DEBUG] 💾 Total workers in dict: {len(self.worker_resources)}")
            print(f"[DEBUG] 💾 Worker IDs in dict: {list(self.worker_resources.keys())}")
        
        # Schedule UI update on Qt main thread
        print(f"[DEBUG] 🔄 Scheduling update_resource_display() on main thread")
        QtCore.QTimer.singleShot(0, self.update_resource_display)
    
    def update_resource_display(self):
        """Update the resource display with current worker data"""
        print(f"[DEBUG] 📺 update_resource_display() called")
        
        # Get snapshot immediately
        snapshot = self._get_worker_resources_snapshot()
        print(f"[DEBUG] 📸 Got snapshot with {len(snapshot)} workers")
        
        # Check if we have data
        if not snapshot:
            connected_workers = self.network.get_connected_workers()
            if not connected_workers:
                print(f"[DEBUG] ⏳ No workers connected")
                self.resource_display.setPlainText(
                    "⏳ Waiting for worker resources...\n\nConnect a worker and resources will appear here."
                )
            else:
                print(f"[DEBUG] ⏳ {len(connected_workers)} workers connected but no data yet")
                self.resource_display.setPlainText(
                    f"✅ Connected to {len(connected_workers)} worker(s)\n\n⏳ Loading resource data..."
                )
            return
        
        # Build display text
        output = []
        output.append(f"📊 LIVE WORKER RESOURCES - {len(snapshot)} Connected")
        output.append(f"🕐 Updated: {time.strftime('%H:%M:%S')}")
        output.append("=" * 50)
        output.append("")
        
        for wid, stats in snapshot.items():
            print(f"[DEBUG] 🔄 Processing worker {wid}")
            # Extract worker IP
            worker_ip = wid.split(":")[0] if ":" in wid else wid
            
            # Get stats
            cpu = stats.get("cpu_percent", 0.0)
            mem_percent = stats.get("memory_percent", 0.0)
            mem_total_mb = stats.get("memory_total_mb", 0.0)
            mem_avail_mb = stats.get("memory_available_mb", 0.0)
            mem_used_mb = mem_total_mb - mem_avail_mb if mem_total_mb > 0 else 0
            disk_percent = stats.get("disk_percent", 0.0)
            disk_free_gb = stats.get("disk_free_gb", 0.0)
            battery = stats.get("battery_percent")
            plugged = stats.get("battery_plugged")
            
            print(f"[DEBUG] 📊 Stats - CPU: {cpu:.1f}%, MEM: {mem_percent:.1f}%, AVAIL: {mem_avail_mb:.0f}MB")
            
            # Status indicator
            def status(val):
                return "🟢" if val < 50 else "🟡" if val < 75 else "🔴"
            
            output.append(f"🖥️  WORKER: {worker_ip}")
            output.append("-" * 50)
            
            # CPU
            output.append(f"{status(cpu)} CPU Usage:          {cpu:5.1f}%")
            
            # Memory - HIGHLIGHT UNUTILIZED RAM
            mem_total_gb = mem_total_mb / 1024
            mem_used_gb = mem_used_mb / 1024
            mem_avail_gb = mem_avail_mb / 1024
            output.append(f"{status(mem_percent)} Memory Usage:       {mem_percent:5.1f}%")
            output.append(f"   • Total RAM:        {mem_total_gb:6.2f} GB")
            output.append(f"   • Used RAM:         {mem_used_gb:6.2f} GB")
            output.append(f"   💚 UNUTILIZED RAM:  {mem_avail_gb:6.2f} GB ⭐")
            
            # Disk
            output.append(f"{status(disk_percent)} Disk Usage:         {disk_percent:5.1f}%")
            output.append(f"   • Free Space:       {disk_free_gb:6.1f} GB")
            
            # Battery
            if battery is not None:
                icon = "🔌" if plugged else "🔋"
                status_text = "Charging" if plugged else "On Battery"
                output.append(f"{icon} Battery:            {battery:5.0f}% ({status_text})")
            else:
                output.append("⚡ Power:              AC (No Battery)")
            
            output.append("")
        
        final_text = "\n".join(output)
        print(f"[DEBUG] 📝 Generated text: {len(final_text)} chars")
        print(f"[DEBUG] 📝 First 150 chars: {final_text[:150]}")
        
        # Update display (we're already on Qt main thread)
        print(f"[DEBUG] 🎨 Updating display widget NOW")
        self.resource_display.setPlainText(final_text)
        print(f"[DEBUG] ✅ Display updated successfully!")

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
            self.resource_display.setPlainText("⚠️  No workers connected.\n\nPlease connect a worker first.")
            return
        
        # Request from all workers
        for worker_id in workers.keys():
            self.network.request_resources_from_worker(worker_id)

    def _get_worker_resources_snapshot(self):
        with self.worker_resources_lock:
            print(f"[DEBUG] 📸 Creating snapshot from {len(self.worker_resources)} stored workers")
            print(f"[DEBUG] 📸 Worker IDs in resources: {list(self.worker_resources.keys())}")
            snapshot = {wid: data.copy() for wid, data in self.worker_resources.items()}
            for wid, data in snapshot.items():
                print(f"[DEBUG]    ✓ Worker {wid}: {len(data)} data fields - CPU: {data.get('cpu_percent', 'N/A')}")
            return snapshot

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
