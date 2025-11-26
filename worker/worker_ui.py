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
        self.setWindowTitle("WinLink – Worker PC")
        
        # Keep window frame but make it custom-styled
        # Using Qt.Window flag allows proper maximize behavior
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Window stays maximized - no dragging variables needed

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
        self.network.set_connection_callback(self.handle_master_connected)

        # Build UI
        self.setup_ui()
        self.update_ip()
        self.start_monitoring_thread()
        # Initial resource update to populate immediately
        QTimer.singleShot(100, self.update_resources_now)

    def handle_master_connected(self, addr):
        """Handle when master connects to worker"""
        connect_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log("─" * 60)
        self.log(f"🔗 Master connected from {addr[0]}:{addr[1]}")
        self.log(f"   ⏱️  Connected at: {connect_time}")
        self.log(f"   ✓ Worker ready to receive tasks")
        self.log("─" * 60)

    def handle_resource_request(self, data):
        try:
            resource_data = self.task_executor.get_system_resources()
            self.network.send_resource_data(resource_data)
        except Exception as e:
            pass

    def handle_heartbeat(self, data):
        msg = NetworkMessage(MessageType.HEARTBEAT_RESPONSE, {
            "timestamp": time.time()
        })
        self.network.send_message_to_master(msg)

    def setup_ui(self):
        self.setStyleSheet(STYLE_SHEET)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Title Bar - hidden since we use system frame now
        # self._create_title_bar()

        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(6)

        # Header
        title = QLabel("WinLink – Worker PC")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)

        # Responsive splitter for panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.addWidget(self.create_connection_panel())
        splitter.addWidget(self.create_task_panel())
        splitter.setSizes([400, 600])
        content_layout.addWidget(splitter, 1)

        # main_layout.addWidget(self.title_bar)  # Hidden - using system frame
        main_layout.addWidget(content_widget, 1)

    def _create_title_bar(self):
        """Create modern custom title bar with controls"""
        self.title_bar = QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 0, 10, 0)
        title_layout.setSpacing(10)
        
        # App icon and title
        app_info_layout = QHBoxLayout()
        app_info_layout.setSpacing(12)
        
        # App icon
        app_icon = QLabel("⚡")
        app_icon.setObjectName("appIcon")
        from PyQt5.QtGui import QFont
        app_icon.setFont(QFont("Segoe UI Emoji", 16))
        app_info_layout.addWidget(app_icon)
        
        # Title
        title_label = QLabel("WinLink - Worker PC (Enhanced)")
        title_label.setObjectName("titleLabel")
        title_font = QFont("Segoe UI", 11, QFont.DemiBold)
        title_label.setFont(title_font)
        app_info_layout.addWidget(title_label)
        
        title_layout.addLayout(app_info_layout)
        title_layout.addStretch()
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)
        
        # Minimize button with proper height
        self.minimize_btn = QPushButton("-")
        self.minimize_btn.setFixedSize(45, 35)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: #555555;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 5px;
                margin-right: 5px;
            }
            QPushButton:hover { 
                background: #666666;
                border: 1px solid #888888;
            }
        """)
        controls_layout.addWidget(self.minimize_btn)
        
        # Close button with proper height
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(45, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #c0392b;
                border-radius: 4px;
            }
            QPushButton:hover { 
                background: #c0392b;
                border: 1px solid #a93226;
            }
        """)
        controls_layout.addWidget(self.close_btn)
        
        title_layout.addLayout(controls_layout)
        
        # Title bar is not draggable - window stays maximized

    # Window stays maximized - no dragging or resizing allowed

    def create_connection_panel(self):
        panel = QFrame()
        panel.setProperty("glass", True)
        layout = QVBoxLayout(panel)
        layout.setSpacing(2)

        # — Connection Settings —
        conn_gb = QGroupBox("Connection Settings")
        conn_layout = QVBoxLayout(conn_gb)
        conn_layout.setContentsMargins(12, 20, 12, 12)
        conn_layout.setSpacing(8)

        self.ip_label = QLabel("IP Address: –")
        self.ip_label.setObjectName("ipLabel")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port (e.g. 5001)")
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setObjectName("portInput")
        # Improve visibility and sizing for input
        self.port_input.setFixedHeight(28)
        p_font = self.port_input.font()
        p_font.setPointSize(max(10, p_font.pointSize()))
        self.port_input.setFont(p_font)
        self.port_input.setStyleSheet("QLineEdit { padding: 6px; color: #e6e6fa; background: rgba(255,255,255,0.06); border-radius: 6px; }")

        conn_layout.addWidget(self.ip_label)
        conn_layout.addWidget(self.port_input)
        layout.addWidget(conn_gb)

        # — Share Resources —
        share_gb = QGroupBox("Share Resources")
        share_gb.setMinimumHeight(200)
        share_gb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        share_layout = QVBoxLayout(share_gb)
        share_layout.setContentsMargins(12, 20, 12, 12)
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

        # --- LIMITS SECTION (Responsive UI) ---
        limits = QFormLayout()
        limits.setContentsMargins(0, 12, 0, 0)
        limits.setHorizontalSpacing(18)

        # Make the form responsive
        limits.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        limits.setLabelAlignment(Qt.AlignLeft)

        spinbox_style = """
        QSpinBox {
            color: #e6e6fa;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 6px;
            font-size: 10pt;
            padding: 4px;
        }
        """

        # CPU SPINBOX
        self.cpu_limit = QSpinBox()
        self.cpu_limit.setRange(10, 100)
        self.cpu_limit.setValue(80)
        self.cpu_limit.setSuffix("%")
        self.cpu_limit.setAlignment(Qt.AlignCenter)
        self.cpu_limit.setStyleSheet(spinbox_style)
        self.cpu_limit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # MEMORY SPINBOX
        self.mem_limit = QSpinBox()
        self.mem_limit.setRange(256, 8192)
        self.mem_limit.setValue(512)
        self.mem_limit.setSuffix(" MB")
        self.mem_limit.setAlignment(Qt.AlignCenter)
        self.mem_limit.setStyleSheet(spinbox_style)
        self.mem_limit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # LABELS
        lbl_cpu = QLabel("Max CPU:")
        lbl_cpu.setObjectName("dataLabel")
        lbl_cpu.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        lbl_mem = QLabel("Max Memory:")
        lbl_mem.setObjectName("dataLabel")
        lbl_mem.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # ROW WRAPPERS TO FORCE PROPER RESIZING
        cpu_row = QWidget()
        cpu_layout = QHBoxLayout(cpu_row)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.addWidget(self.cpu_limit)
        cpu_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        mem_row = QWidget()
        mem_layout = QHBoxLayout(mem_row)
        mem_layout.setContentsMargins(0, 0, 0, 0)
        mem_layout.addWidget(self.mem_limit)
        mem_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add rows
        limits.addRow(lbl_cpu, cpu_row)
        limits.addRow(lbl_mem, mem_row)

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
        # Give the start button more padding and height for better visibility
        self.start_btn.setMinimumHeight(40)  # Taller button
        self.start_btn.setMinimumWidth(120)  # Reasonable minimum width
        self.start_btn.setStyleSheet("QPushButton#startBtn { padding: 8px 16px; font-size: 10pt; font-weight: bold; }")

        self.stop_btn = QPushButton("Stop Worker")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.clicked.connect(self.stop_worker)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)  # Taller button
        self.stop_btn.setMinimumWidth(120)  # Reasonable minimum width
        self.stop_btn.setStyleSheet("QPushButton#stopBtn { padding: 8px 16px; font-size: 10pt; font-weight: bold; }")

        # Container to add top margin above the buttons and keep them stacked
        btn_container = QFrame()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 15, 0, 0)  # More top margin
        btn_layout.setSpacing(12)  # Better spacing between buttons
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addWidget(btn_container)

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
        v.setContentsMargins(8, 20, 8, 8)
        self.tasks_display = QTextEdit()
        self.tasks_display.setObjectName("tasksDisplay")
        self.tasks_display.setReadOnly(True)
        self.tasks_display.setPlainText("No active tasks.")
        self.tasks_display.setMinimumHeight(70)
        self.tasks_display.setMaximumHeight(100)
        # Improve font for better readability - larger font for active tasks
        tasks_font = self.tasks_display.font()
        tasks_font.setFamily("Segoe UI")
        tasks_font.setBold(True)  # Make it bold for better visibility
        self.tasks_display.setFont(tasks_font)
        # Override any CSS font settings to ensure our font size is applied
        self.tasks_display.setStyleSheet("""
            QTextEdit#tasksDisplay {
                background-color: rgba(30, 30, 40, 0.8);
                color: #f0f0f0;
                border: 2px solid rgba(100, 255, 160, 0.4);
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
                line-height: 1.3;
            }
        """)
        v.addWidget(self.tasks_display)
        layout.addWidget(tasks_gb)
        
        # Task Output Display
        output_gb = QGroupBox("Task Output")
        ov = QVBoxLayout(output_gb)
        ov.setContentsMargins(8, 20, 8, 8)
        self.task_output_display = QTextEdit()
        self.task_output_display.setObjectName("tasksDisplay")
        self.task_output_display.setReadOnly(True)
        self.task_output_display.setPlainText("No task output yet.")
        self.task_output_display.setMinimumHeight(100)  # Increased height
        self.task_output_display.setMaximumHeight(150)  # Increased max height
        # Enhanced font for much better readability - smaller font for placeholder text
        output_font = self.task_output_display.font()
        output_font.setFamily("Consolas")  # Monospace for better code/output readability
        self.task_output_display.setFont(output_font)
        # Better styling for output display
        self.task_output_display.setStyleSheet("""
            QTextEdit#tasksDisplay {
                background-color: rgba(30, 30, 40, 0.8);
                color: #f0f0f0;
                border: 2px solid rgba(100, 255, 160, 0.4);
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
                line-height: 1.3;
            }
        """)
        ov.addWidget(self.task_output_display)
        layout.addWidget(output_gb)

        # System Resources - Enhanced UI
        res_gb = QGroupBox("💻 System Resources (Real-time)")
        rv = QVBoxLayout(res_gb)
        rv.setContentsMargins(12, 20, 12, 12)
        rv.setSpacing(12)

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
        self.res_details.setMinimumHeight(160)
        self.res_details.setMaximumHeight(160)
        res_font = self.res_details.font()
        res_font.setPointSize(9)
        res_font.setFamily("Consolas")
        self.res_details.setFont(res_font)
        self.res_details.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 25, 35, 0.9);
                color: #e8e8e8;
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                padding: 10px;
                font-size: 9pt;
                line-height: 1.4;
            }
        """)
        rv.addWidget(self.res_details)

        layout.addWidget(res_gb)

        # Task Log - Enhanced styling and better visibility
        log_gb = QGroupBox("📋 Task Execution Log")
        lv = QVBoxLayout(log_gb)
        lv.setContentsMargins(12, 15, 12, 12)  # Better margins
        lv.setSpacing(10)  # Increased spacing

        self.task_log = QTextEdit()
        self.task_log.setReadOnly(True)
        # Better size constraints for log visibility
        self.task_log.setMinimumHeight(120)  # Increased minimum height
        self.task_log.setMaximumHeight(400)  # Reasonable maximum height
        self.task_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.task_log.setPlainText("📝 Task Execution Log\n" + "─" * 60 + "\nTask execution details will appear here...\nYou will see: task received, started, progress, completion time, and results.")
        # Enhanced font and styling for task log
        log_font = self.task_log.font()
        log_font.setPointSize(9)  # Slightly larger font
        log_font.setFamily("Consolas")  # Monospace for log readability
        self.task_log.setFont(log_font)
        # Better styling for the log area
        self.task_log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 20, 30, 0.9);
                color: #e8e8e8;
                border: 2px solid rgba(100, 255, 160, 0.3);
                border-radius: 10px;
                padding: 12px;
                font-size: 9pt;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid rgba(100, 255, 160, 0.6);
            }
        """)

        # Enhanced buttons section with better styling
        btns = QHBoxLayout()
        btns.setContentsMargins(0, 10, 0, 0)
        btns.setSpacing(12)
        
        # Clear button with icon
        c = QPushButton("🗑️ Clear Log")
        c.clicked.connect(self.task_log.clear)
        c.setMinimumHeight(42)
        c.setMinimumWidth(110)
        c.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.8);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 9pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(255, 120, 120, 0.9);
            }
        """)
        
        # Export button with icon
        e = QPushButton("📤 Export Log")
        e.clicked.connect(self.export_log)
        e.setMinimumHeight(42)
        e.setMinimumWidth(110)
        e.setStyleSheet("""
            QPushButton {
                background: rgba(100, 150, 255, 0.8);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 9pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(120, 170, 255, 0.9);
            }
        """)
        
        btns.addWidget(c)
        btns.addWidget(e)
        btns.addStretch()  # Push buttons to the left

        lv.addWidget(self.task_log)
        lv.addLayout(btns)
        layout.addWidget(log_gb)

        self.apply_shadow(panel)
        return panel

    def _make_bar(self, text, color):
        h = QHBoxLayout()
        h.setSpacing(8)
        
        # Label with smaller font for better fit
        lbl = QLabel(text)
        lbl.setMinimumWidth(100)
        lbl.setObjectName("infoLabel")
        lbl_font = lbl.font()
        lbl_font.setPointSize(9)
        lbl_font.setBold(True)
        lbl.setFont(lbl_font)
        lbl.setStyleSheet("color: #e6e6fa; font-size: 9pt;")

        # Progress bar with compact styling
        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setMaximumHeight(18)
        bar.setMinimumHeight(18)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 9px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color}, stop:1 {color}CC);
                border-radius: 7px;
            }}
        """)

        # Value label with smaller font
        val = QLabel("0%")
        val.setMinimumWidth(100)
        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val_font = val.font()
        val_font.setPointSize(9)
        val_font.setBold(True)
        val.setFont(val_font)
        val.setStyleSheet("color: #ffffff; font-size: 9pt; padding-left: 5px;")

        h.addWidget(lbl)
        h.addWidget(bar, 1)  # Bar stretches
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
            
            # Detailed start log
            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            hostname = socket.gethostname()
            self.log("─" * 60)
            self.log(f"🚀 Worker started at {start_time}")
            self.log(f"   💻 Hostname: {hostname}")
            self.log(f"   🌐 IP Address: {self.network.ip}")
            self.log(f"   🔌 Port: {port}")
            self.log(f"   ✓ Status: Ready to accept tasks")
            self.log("─" * 60)
        else:
            QMessageBox.critical(self, "Error", "Failed to start.")

    def stop_worker(self):
        self.network.stop()
        self.status_label.setText("Status: 🔴 Idle")
        self.conn_str.setText("N/A")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Detailed stop log
        stop_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log("─" * 60)
        self.log(f"🛑 Worker stopped at {stop_time}")
        self.log(f"   ✓ All connections closed")
        self.log(f"   ✓ Server shutdown complete")
        self.log("─" * 60)

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
            self._send_error_to_master(task_id or "unknown", "Invalid task payload received by worker.")
            return
        
        # Log task received with timestamp
        task_name = data.get("name", "Unnamed Task")
        receive_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"📥 Task received: '{task_name}' [ID: {task_id[:8]}...] at {receive_time}")
        
        # Immediately show the task in the UI - ensure it's visible right away
        with self.tasks_lock:
            self.current_tasks[task_id] = {
                "status": "pending",
                "progress": 0,
                "started_at": None,
                "memory_used_mb": 0,
                "output": None,
                "name": task_name
            }
        # Schedule UI updates on the Qt main thread
        QTimer.singleShot(0, self._refresh_tasks_display)
        QTimer.singleShot(0, self._refresh_output_display)

        def run_task():
            start_time = time.time()
            start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
            self._set_task_state(task_id, status="running", progress=0, started_at=start_time)
            self.log(f"▶️ Task started: '{task_name}' [ID: {task_id[:8]}...] at {start_time_str}")
            self.send_progress_update(task_id, 0)

            def progress_with_log(pct):
                # Log significant progress milestones
                if pct in [25, 50, 75]:
                    self.log(f"⏳ Task '{task_name}' [{task_id[:8]}...] progress: {pct}%")
                self.send_progress_update(task_id, pct)
            
            result = self.task_executor.execute_task(
                code,
                payload,
                progress_callback=progress_with_log
            )

            status = "done" if result.get("success") else "failed"
            progress_final = 100 if result.get("success") else max(0, min(99, self._get_task_progress(task_id)))
            self.send_progress_update(task_id, progress_final)
            
            # Calculate execution time
            end_time = time.time()
            end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
            execution_time = result.get("execution_time", end_time - start_time)
            memory_used = result.get("memory_used", 0)
            
            # Log task completion or failure with detailed information
            if result.get("success"):
                self.log(f"✅ Task completed: '{task_name}' [ID: {task_id[:8]}...]")
                self.log(f"   ⏱️  Ended at: {end_time_str}")
                self.log(f"   ⏱️  Execution time: {execution_time:.2f}s")
                self.log(f"   💾 Memory used: {memory_used:.2f} MB")
                self.log(f"   ✓ Status: SUCCESS (100%)")
            else:
                error_msg = result.get("error", "Unknown error")
                self.log(f"❌ Task failed: '{task_name}' [ID: {task_id[:8]}...]")
                self.log(f"   ⏱️  Ended at: {end_time_str}")
                self.log(f"   ⏱️  Execution time: {execution_time:.2f}s")
                self.log(f"   💾 Memory used: {memory_used:.2f} MB")
                self.log(f"   ✗ Error: {error_msg[:100]}")
            self.log("─" * 60)  # Separator line for readability

            # Build output text
            output_parts = []
            if result.get("stdout"):
                output_parts.append(f"STDOUT:\n{result['stdout']}")
            if result.get("stderr"):
                output_parts.append(f"STDERR:\n{result['stderr']}")
            
            # Handle result display with better formatting
            result_val = result.get("result")
            if result_val is not None:
                if isinstance(result_val, dict):
                    if result_val:  # Non-empty dict
                        output_parts.append(f"RESULT:\n{json.dumps(result_val, indent=2)}")
                    else:
                        output_parts.append(f"RESULT:\n{{}}")
                elif isinstance(result_val, (list, tuple)):
                    if result_val:
                        output_parts.append(f"RESULT:\n{json.dumps(result_val, indent=2)}")
                    else:
                        output_parts.append(f"RESULT:\n[]")
                elif isinstance(result_val, str):
                    if result_val:
                        output_parts.append(f"RESULT:\n{result_val}")
                    else:
                        output_parts.append(f"RESULT:\n(empty string)")
                elif isinstance(result_val, bool):
                    output_parts.append(f"RESULT:\n{result_val}")
                elif isinstance(result_val, (int, float)):
                    output_parts.append(f"RESULT:\n{result_val}")
                else:
                    output_parts.append(f"RESULT:\n{str(result_val)}")
            else:
                # result is None - check if task succeeded
                if result.get("success") and not result.get("error"):
                    output_parts.append("RESULT:\n(Task completed but returned None)")
            
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
                    if stats:
                        # Create a new method invocation each time to avoid capture issues
                        from functools import partial
                        callback = partial(self._update_resources, stats.copy())
                        QTimer.singleShot(0, callback)
                except Exception as exc:
                    pass
        threading.Thread(target=monitor, daemon=True).start()

    def update_resources_now(self):
        """Force an immediate resource update"""
        try:
            stats = self.task_executor.get_system_resources()
            if stats:
                self._update_resources(stats)
        except Exception as exc:
            pass

    def _update_resources(self, r):
        """Update UI with real-time resource data"""
        if not r:
            return
            
        cpu = r.get('cpu_percent', 0.0)
        mem = r.get('memory_percent', 0.0)
        disk = r.get('disk_percent', 0.0)
        battery = r.get('battery_percent')
        plugged = r.get('battery_plugged')

        # Read configured limits
        try:
            cpu_limit_val = int(self.cpu_limit.value())
        except Exception:
            cpu_limit_val = 100
        try:
            mem_limit_val = int(self.mem_limit.value())
        except Exception:
            mem_limit_val = 8192

        # Update bars with actual usage
        try:
            self.cpu_bar.setValue(int(cpu))
            self.cpu_label.setText(f"{cpu:.1f}% (limit {cpu_limit_val}%)")

            self.mem_bar.setValue(int(mem))
            self.mem_label.setText(f"{mem:.1f}% (limit {mem_limit_val} MB)")
            
            self.disk_bar.setValue(int(disk))
            self.disk_label.setText(f"{disk:.1f}%")
        except Exception as e:
            pass

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
        
        # Get additional real-time metrics
        mem_total_gb = psutil.virtual_memory().total / (1024**3)
        mem_used_gb = psutil.virtual_memory().used / (1024**3)
        mem_available_mb = r.get('memory_available_mb', 0)
        disk_free_gb = r.get('disk_free_gb', 0)
        
        # CPU per-core usage (if available)
        try:
            cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
            cpu_cores_info = ", ".join([f"{c:.0f}%" for c in cpu_per_core[:4]])  # Show first 4 cores
            if len(cpu_per_core) > 4:
                cpu_cores_info += "..."
        except:
            cpu_cores_info = "N/A"
        
        details = (
            f"💻 CPU\n"
            f"  Cores: {psutil.cpu_count(logical=False)} Physical | {psutil.cpu_count()} Logical\n"
            f"  Usage: {cpu:.1f}% | Limit: {cpu_limit_val}%\n"
            f"  Per-core: {cpu_cores_info}\n"
            f"\n"
            f"🧠 Memory\n"
            f"  Total: {mem_total_gb:.2f} GB | Used: {mem_used_gb:.2f} GB ({mem:.1f}%)\n"
            f"  Available: {mem_available_mb:.0f} MB | Limit: {mem_limit_val} MB\n"
            f"  Tasks Memory: {task_memory_mb:.1f} MB\n"
            f"\n"
            f"💾 Disk\n"
            f"  Usage: {disk:.1f}% | Free: {disk_free_gb:.1f} GB\n"
            f"\n"
            f"🔋 Battery: {battery_str}\n"
            f"⚡ Active Tasks: {active_tasks}"
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
            pass
        finally:
            e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WorkerUI()
    sys.exit(app.exec_())
