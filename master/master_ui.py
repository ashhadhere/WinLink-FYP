import sys, os, json, threading, time
from typing import Optional
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QHeaderView, QSplitter, QPushButton, QComboBox, QListWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from assets.styles import STYLE_SHEET
from core.task_manager import TaskManager, TASK_TEMPLATES, TaskStatus, TaskType
from core.network import MasterNetwork, MessageType

class MasterUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Master PC")

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
        icon_path = os.path.join(ROOT, "assets", "WinLink_logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet(STYLE_SHEET)

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

        self.setup_ui()
        self.start_monitoring_thread()

        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self.refresh_discovered_workers)
        self.discovery_timer.start(2000)  # Refresh every 2 seconds

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_widget = QtWidgets.QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

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
        content_layout.addWidget(splitter)

        main_layout.addWidget(content_widget, 1)

    def _create_title_bar(self):
        """Create modern custom title bar with controls"""
        self.title_bar = QtWidgets.QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(50)
        
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 0, 10, 0)
        title_layout.setSpacing(10)

        app_info_layout = QtWidgets.QHBoxLayout()
        app_info_layout.setSpacing(12)

        app_icon = QtWidgets.QLabel("🎯")
        app_icon.setObjectName("appIcon")
        app_icon.setFont(QtGui.QFont("Segoe UI Emoji", 16))
        app_info_layout.addWidget(app_icon)

        title_label = QtWidgets.QLabel("WinLink - Master PC (Enhanced)")
        title_label.setObjectName("titleLabel")
        title_font = QtGui.QFont("Segoe UI", 11, QtGui.QFont.DemiBold)
        title_label.setFont(title_font)
        app_info_layout.addWidget(title_label)
        
        title_layout.addLayout(app_info_layout)
        title_layout.addStretch()

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setSpacing(0)

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

    def create_worker_panel(self):
        panel = QtWidgets.QFrame()
        panel.setProperty("glass", True)
        lay = QtWidgets.QVBoxLayout(panel)
        lay.setSpacing(12)
        lay.setContentsMargins(10, 15, 10, 10)

        hdr = QtWidgets.QLabel("🖥️ Worker Management", panel)
        hdr.setObjectName("headerLabel")
        hdr.setAlignment(QtCore.Qt.AlignCenter)
        hf = hdr.font()
        hf.setPointSize(13)
        hf.setBold(True)
        hdr.setFont(hf)
        hdr.setMargin(6)
        lay.addWidget(hdr)

        grp = QtWidgets.QGroupBox("⚡ Add Worker", panel)
        g_l = QtWidgets.QVBoxLayout(grp)
        g_l.setSpacing(8)
        g_l.setContentsMargins(10, 18, 10, 10)

        disco_label = QtWidgets.QLabel("🔍 Select Workers:")
        disco_label.setStyleSheet("font-size: 9pt; font-weight: 600; color: #00f5a0; margin-bottom: 3px;")
        g_l.addWidget(disco_label)

        help_text = QtWidgets.QLabel("Click dropdown to select multiple workers • Auto-refreshes every 2s")
        help_text.setStyleSheet("font-size: 8pt; color: rgba(255, 255, 255, 0.5); margin-bottom: 5px;")
        g_l.addWidget(help_text)

        self.discovered_combo = QComboBox()
        self.discovered_combo.setMinimumHeight(36)

        combo_model = QtGui.QStandardItemModel()
        self.discovered_combo.setModel(combo_model)

        list_view = QtWidgets.QListView()
        list_view.setStyleSheet("""
            QListView::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListView::item:hover {
                background: rgba(0, 245, 160, 0.15);
            }
        """)
        self.discovered_combo.setView(list_view)

        combo_model.dataChanged.connect(self._on_combo_selection_changed)
        
        self.discovered_combo.setStyleSheet("""
            QComboBox {
                background: rgba(15, 20, 30, 0.95);
                color: #e6e6fa;
                border: 2px solid rgba(0, 245, 160, 0.25);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 9pt;
            }
            QComboBox:hover {
                border: 2px solid rgba(0, 245, 160, 0.4);
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #00f5a0;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: rgba(20, 25, 35, 0.98);
                color: #e6e6fa;
                selection-background-color: rgba(0, 245, 160, 0.25);
                border: 2px solid rgba(0, 245, 160, 0.4);
                border-radius: 6px;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 10px;
                border-radius: 4px;
                margin: 1px 2px;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(0, 245, 160, 0.15);
            }
        """)
        
        g_l.addWidget(self.discovered_combo)

        connect_btns_layout = QtWidgets.QHBoxLayout()
        connect_btns_layout.setSpacing(6)
        
        self.connect_discovered_btn = QtWidgets.QPushButton("Connect Selected")
        self.connect_discovered_btn.setObjectName("startBtn")
        self.connect_discovered_btn.setMinimumHeight(36)
        self.connect_discovered_btn.setEnabled(False)
        self.connect_discovered_btn.clicked.connect(self.connect_from_list)
        self.connect_discovered_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 245, 160, 0.7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(0, 245, 160, 0.85);
            }
            QPushButton:pressed {
                background: rgba(0, 245, 160, 0.6);
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 0.3);
                color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        self.connect_all_btn = QtWidgets.QPushButton("Connect All")
        self.connect_all_btn.setMinimumHeight(36)
        self.connect_all_btn.setEnabled(False)
        self.connect_all_btn.clicked.connect(self.connect_all_discovered)
        self.connect_all_btn.setStyleSheet("""
            QPushButton {
                background: rgba(102, 126, 234, 0.7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.85);
            }
            QPushButton:pressed {
                background: rgba(102, 126, 234, 0.6);
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 0.3);
                color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        connect_btns_layout.addWidget(self.connect_discovered_btn, 1)
        connect_btns_layout.addWidget(self.connect_all_btn, 1)
        g_l.addLayout(connect_btns_layout)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("background: rgba(255, 255, 255, 0.15); margin: 12px 0px 10px 0px; max-height: 1px;")
        g_l.addWidget(sep)

        manual_label = QtWidgets.QLabel("✏️ Manual Entry:")
        manual_label.setStyleSheet("font-size: 9pt; font-weight: 600; color: #667eea; margin-bottom: 5px;")
        g_l.addWidget(manual_label)

        manual_input_layout = QtWidgets.QHBoxLayout()
        manual_input_layout.setSpacing(6)
        
        self.ip_input = QtWidgets.QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")
        self.ip_input.setMinimumHeight(34)
        self.ip_input.setStyleSheet("""
            QLineEdit {
                background: rgba(25, 30, 40, 0.9);
                color: #e6e6fa;
                border: 2px solid rgba(102, 126, 234, 0.25);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 0.5);
                background: rgba(25, 30, 40, 1);
            }
            QLineEdit:hover {
                border: 2px solid rgba(102, 126, 234, 0.35);
            }
        """)
        
        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setValidator(QtGui.QIntValidator(1, 65535))
        self.port_input.setMinimumHeight(34)
        self.port_input.setFixedWidth(90)
        self.port_input.setStyleSheet(self.ip_input.styleSheet())
        
        manual_input_layout.addWidget(self.ip_input, 2)
        manual_input_layout.addWidget(self.port_input, 0)
        g_l.addLayout(manual_input_layout)
        
        self.connect_btn = QtWidgets.QPushButton("🔌 Connect")
        self.connect_btn.setObjectName("startBtn")
        self.connect_btn.setMinimumHeight(36)
        self.connect_btn.clicked.connect(self.connect_to_worker)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: rgba(102, 126, 234, 0.7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.85);
            }
            QPushButton:pressed {
                background: rgba(102, 126, 234, 0.6);
            }
        """)
        
        g_l.addWidget(self.connect_btn)
        lay.addWidget(grp)

        wgrp = QtWidgets.QGroupBox("Connected Workers", panel)
        w_l = QtWidgets.QVBoxLayout(wgrp)
        w_l.setSpacing(6)
        w_l.setContentsMargins(8, 20, 8, 8)
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

        rgrp = QtWidgets.QGroupBox("Live Worker Resources", panel)
        r_l = QtWidgets.QVBoxLayout(rgrp)
        r_l.setSpacing(6)
        r_l.setContentsMargins(8, 20, 8, 8)
        self.resource_display = QtWidgets.QTextEdit()
        self.resource_display.setReadOnly(True)
        self.resource_display.setMinimumHeight(150)

        font = self.resource_display.font()
        font.setPointSize(9)  # Comfortable font size
        font.setFamily("Consolas")  # Monospace font for alignment
        self.resource_display.setFont(font)

        self.resource_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 40, 0.8);
                color: #f0f0f0;
                border: 1px solid rgba(100, 255, 160, 0.5);
                border-radius: 8px;
                padding: 10px;
                font-size: 9pt;
            }
        """)
        self.resource_display.setPlainText("⏳ Waiting for worker resources...\n\nConnect a worker and resources will appear here.")
        r_l.addWidget(self.resource_display)

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
        lay.setContentsMargins(10, 15, 10, 10)

        hdr = QtWidgets.QLabel("📋 Task Management", panel)
        hdr.setObjectName("headerLabel"); hdr.setAlignment(QtCore.Qt.AlignCenter)
        hf = hdr.font()
        hf.setPointSize(13)
        hf.setBold(True)
        hdr.setFont(hf)
        hdr.setMargin(6)
        lay.addWidget(hdr)

        grp = QtWidgets.QGroupBox("Create Task", panel)
        g_l = QtWidgets.QVBoxLayout(grp)
        g_l.setSpacing(6)
        g_l.setContentsMargins(8, 15, 8, 8)

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

        desc_font = self.task_description.font()
        desc_font.setPointSize(9)
        desc_font.setBold(True)
        self.task_description.setFont(desc_font)
        self.task_description.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                background-color: rgba(50, 50, 70, 0.5);
                border-radius: 4px;
                padding: 6px;
                margin: 4px 0;
            }
        """)
        g_l.addWidget(self.task_description)
        self.task_code_edit = QtWidgets.QTextEdit(); self.task_code_edit.setMaximumHeight(120)

        code_font = self.task_code_edit.font()
        code_font.setPointSize(9)
        code_font.setFamily("Consolas")
        self.task_code_edit.setFont(code_font)
        g_l.addWidget(self.task_code_edit)
        self.task_data_edit = QtWidgets.QTextEdit(); self.task_data_edit.setMaximumHeight(80)

        data_font = self.task_data_edit.font()
        data_font.setPointSize(9)
        data_font.setFamily("Consolas")
        self.task_data_edit.setFont(data_font)
        g_l.addWidget(self.task_data_edit)

        editor_style = """
            QTextEdit {
                background-color: rgba(30, 30, 40, 0.9);
                color: #f0f0f0;
                border: 2px solid rgba(100, 255, 160, 0.3);
                border-radius: 6px;
                padding: 8px;
                font-size: 9pt;
                font-family: 'Consolas';
                line-height: 1.3;
            }
            QTextEdit:focus {
                border: 2px solid rgba(100, 255, 160, 0.6);
            }
        """
        self.task_code_edit.setStyleSheet(editor_style)
        self.task_data_edit.setStyleSheet(editor_style)
        
        self.submit_task_btn = QtWidgets.QPushButton("Submit Task"); self.submit_task_btn.setObjectName("startBtn")
        self.submit_task_btn.clicked.connect(self.submit_task)
        g_l.addWidget(self.submit_task_btn)
        lay.addWidget(grp)

        self.on_task_type_changed()

        tgrp = QtWidgets.QGroupBox("📋 Task Queue", panel)
        t_l = QtWidgets.QVBoxLayout(tgrp)
        t_l.setSpacing(8)
        t_l.setContentsMargins(10, 18, 10, 10)

        self.tasks_table = QtWidgets.QTableWidget(0, 7)
        self.tasks_table.setHorizontalHeaderLabels(["ID", "Type", "Status", "Worker", "Progress", "Result", "Output"])

        self.tasks_table.setColumnWidth(0, 80)   # ID
        self.tasks_table.setColumnWidth(1, 100)  # Type
        self.tasks_table.setColumnWidth(2, 90)   # Status
        self.tasks_table.setColumnWidth(3, 130)  # Worker
        self.tasks_table.setColumnWidth(4, 100)  # Progress
        self.tasks_table.setColumnWidth(5, 150)  # Result

        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tasks_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tasks_table.setWordWrap(True)
        self.tasks_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tasks_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tasks_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tasks_table.setMinimumHeight(200)

        header = self.tasks_table.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Output stretches
        header.setStretchLastSection(True)
        hf = header.font()
        hf.setBold(True)
        hf.setPointSize(9)
        header.setFont(hf)
        header.setMinimumHeight(32)

        self.tasks_table.verticalHeader().setVisible(False)
        self.tasks_table.verticalHeader().setDefaultSectionSize(40)

        self.tasks_table.setStyleSheet("""
            QTableWidget {
                background: rgba(15, 20, 30, 0.95);
                color: #e6e6fa;
                border: 2px solid rgba(100, 255, 160, 0.25);
                border-radius: 6px;
                gridline-color: rgba(255, 255, 255, 0.08);
                font-size: 9pt;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background: rgba(0, 245, 160, 0.2);
                color: white;
            }
            QTableWidget::item:hover {
                background: rgba(0, 245, 160, 0.1);
            }
            QHeaderView::section {
                background: rgba(30, 35, 45, 0.95);
                color: #00f5a0;
                padding: 8px;
                border: none;
                border-bottom: 2px solid rgba(0, 245, 160, 0.3);
                font-weight: bold;
                font-size: 9pt;
            }
            QHeaderView::section:hover {
                background: rgba(40, 45, 55, 0.95);
            }
        """)
        
        t_l.addWidget(self.tasks_table)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(8)

        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(34)
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self.refresh_task_table_async)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: rgba(102, 126, 234, 0.7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.85);
            }
            QPushButton:pressed {
                background: rgba(102, 126, 234, 0.6);
            }
        """)

        clear_btn = QtWidgets.QPushButton("🗑️ Clear Completed")
        clear_btn.setObjectName("stopBtn")
        clear_btn.setMinimumHeight(34)
        clear_btn.setFixedWidth(150)
        clear_btn.clicked.connect(self.clear_completed_tasks)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255, 120, 120, 0.85);
            }
            QPushButton:pressed {
                background: rgba(255, 100, 100, 0.6);
            }
        """)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        
        t_l.addLayout(btn_layout)
        lay.addWidget(tgrp)

        return panel

    def start_monitoring_thread(self):
        def monitor():
            while self.monitoring_active:
                workers = self.network.get_connected_workers()
                if workers:
                    for worker_id in workers.keys():
                        self.network.request_resources_from_worker(worker_id)
                time.sleep(10)
        threading.Thread(target=monitor, daemon=True).start()

    def on_worker_selection_changed(self):
        self.disconnect_btn.setEnabled(bool(self.workers_list.selectedItems()))
    
    def refresh_discovered_workers(self):
        """Update the dropdown with newly discovered workers"""
        discovered = self.network.get_discovered_workers()

        checked_workers = []
        for i in range(self.discovered_combo.count()):
            item = self.discovered_combo.model().item(i)
            if item and item.checkState() == QtCore.Qt.Checked:
                worker_info_json = item.data(Qt.UserRole)
                if worker_info_json:
                    try:
                        checked_workers.append(json.loads(worker_info_json))
                    except (json.JSONDecodeError, TypeError):
                        pass

        model = self.discovered_combo.model()
        model.clear()
        
        if not discovered:
            item = QtGui.QStandardItem("🔍 Searching for workers...")
            item.setEnabled(False)
            model.appendRow(item)
            self.discovered_combo.setEnabled(False)
            self.connect_discovered_btn.setEnabled(False)
            self.connect_all_btn.setEnabled(False)
            return
        
        self.discovered_combo.setEnabled(True)
        selected_count = 0
        has_unconnected = False

        for worker_id, info in discovered.items():
            hostname = info.get('hostname', 'Unknown')
            ip = info.get('ip', '')
            port = info.get('port', '')

            connected = worker_id in self.network.get_connected_workers()
            
            if connected:
                display_text = f"✅ {hostname} ({ip}:{port})"
            else:
                display_text = f"🖥️ {hostname} ({ip}:{port})"
                has_unconnected = True

            item = QtGui.QStandardItem(display_text)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckable(True)

            item.setData(json.dumps(info), Qt.UserRole)

            if info in checked_workers:
                item.setCheckState(QtCore.Qt.Checked)
                selected_count += 1
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            if connected:
                item.setEnabled(False)
            
            model.appendRow(item)

        self._update_combo_text()

        self._update_connect_button_states()
        self.connect_all_btn.setEnabled(has_unconnected)
    
    def _on_combo_selection_changed(self):
        """Handle when checkbox states change in the combo box"""
        print("[MASTER] _on_combo_selection_changed called")

        self._update_combo_text()

        self._update_connect_button_states()
    
    def _update_connect_button_states(self):
        """Update the enabled state of connect buttons based on checked items"""
        checked_count = 0
        for i in range(self.discovered_combo.count()):
            item = self.discovered_combo.model().item(i)
            if item and item.checkState() == QtCore.Qt.Checked and item.isEnabled():
                checked_count += 1
        
        print(f"[MASTER] _update_connect_button_states: {checked_count} items checked")

        self.connect_discovered_btn.setEnabled(checked_count > 0)
        print(f"[MASTER] Connect button enabled: {checked_count > 0}")
    
    def _update_combo_text(self):
        """Update combo box display text based on selections"""
        checked_count = 0
        for i in range(self.discovered_combo.count()):
            item = self.discovered_combo.model().item(i)
            if item and item.checkState() == QtCore.Qt.Checked:
                checked_count += 1
        
        if checked_count == 0:
            self.discovered_combo.setCurrentIndex(0)
        elif checked_count == 1:

            for i in range(self.discovered_combo.count()):
                item = self.discovered_combo.model().item(i)
                if item and item.checkState() == QtCore.Qt.Checked:
                    self.discovered_combo.setCurrentIndex(i)
                    break
        else:

            self.discovered_combo.setCurrentText(f"✅ {checked_count} workers selected")
    
    def connect_from_list(self):
        """Connect to selected workers from discovered dropdown"""
        print("[MASTER] connect_from_list called")

        selected_workers = []
        model = self.discovered_combo.model()
        
        print(f"[MASTER] Combo box has {self.discovered_combo.count()} items")
        
        for i in range(self.discovered_combo.count()):
            item = model.item(i)
            if item:
                is_checked = item.checkState() == QtCore.Qt.Checked
                is_enabled = item.isEnabled()
                print(f"[MASTER] Item {i}: checked={is_checked}, enabled={is_enabled}, text={item.text()}")
                
                if is_checked:
                    worker_info_json = item.data(Qt.UserRole)
                    if worker_info_json:
                        try:
                            worker_info = json.loads(worker_info_json)
                            selected_workers.append(worker_info)
                            print(f"[MASTER] Added worker: {worker_info.get('hostname', 'Unknown')}")
                        except (json.JSONDecodeError, TypeError) as e:
                            print(f"[MASTER] Error parsing worker info: {e}")
        
        print(f"[MASTER] Total selected workers: {len(selected_workers)}")
        
        if not selected_workers:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please check at least one worker from the dropdown")
            return
        
        success_count = 0
        fail_count = 0
        already_connected = 0
        
        for worker_info in selected_workers:
            ip = worker_info.get('ip')
            port = worker_info.get('port')
            hostname = worker_info.get('hostname', 'Unknown')
            worker_id = f"{ip}:{port}"

            if worker_id in self.network.get_connected_workers():
                already_connected += 1
                continue
            
            connected = self.network.connect_to_worker(worker_id, ip, int(port))
            if connected:
                success_count += 1

                QtCore.QTimer.singleShot(300, lambda wid=worker_id: self.network.request_resources_from_worker(wid))
            else:
                fail_count += 1

        msg_parts = []
        if success_count > 0:
            msg_parts.append(f"✅ Connected: {success_count}")
        if already_connected > 0:
            msg_parts.append(f"ℹ️ Already connected: {already_connected}")
        if fail_count > 0:
            msg_parts.append(f"❌ Failed: {fail_count}")
        
        if msg_parts:
            QtWidgets.QMessageBox.information(self, "Connection Results", "\n".join(msg_parts))
        
        self.refresh_workers_async()
        self.refresh_discovered_workers()
    
    def connect_all_discovered(self):
        """Connect to all discovered workers"""
        discovered = self.network.get_discovered_workers()
        
        if not discovered:
            QtWidgets.QMessageBox.warning(self, "No Workers", "No workers discovered yet")
            return
        
        success_count = 0
        fail_count = 0
        already_connected = 0
        
        for worker_id, info in discovered.items():

            if worker_id in self.network.get_connected_workers():
                already_connected += 1
                continue
            
            ip = info.get('ip')
            port = info.get('port')
            
            connected = self.network.connect_to_worker(worker_id, ip, int(port))
            if connected:
                success_count += 1

                QtCore.QTimer.singleShot(300, lambda wid=worker_id: self.network.request_resources_from_worker(wid))
            else:
                fail_count += 1

        msg_parts = []
        if success_count > 0:
            msg_parts.append(f"✅ Connected: {success_count}")
        if already_connected > 0:
            msg_parts.append(f"ℹ️ Already connected: {already_connected}")
        if fail_count > 0:
            msg_parts.append(f"❌ Failed: {fail_count}")
        
        if msg_parts:
            QtWidgets.QMessageBox.information(self, "Bulk Connection Results", "\n".join(msg_parts))
        
        self.refresh_workers_async()
        self.refresh_discovered_workers()

    def connect_to_worker(self):
        """Connect to worker using manual IP and port entry"""
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        if not ip or not port:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Enter both IP and Port")
            return
        worker_id = f"{ip}:{port}"

        if worker_id in self.network.get_connected_workers():
            QtWidgets.QMessageBox.information(self, "Already Connected", 
                f"Already connected to {worker_id}")
            return

        self.resource_display.setPlainText(f"🔄 Connecting to {worker_id}...\n\nRetrying up to 3 times if needed...")
        QtWidgets.QApplication.processEvents()
        
        connected = self.network.connect_to_worker(worker_id, ip, int(port))
        if not connected:
            error_msg = (
                f"Failed to connect to {worker_id} after 3 attempts\n\n"
                "Common fixes:\n"
                "1. Ensure Worker app is running and 'Start Worker' is clicked\n"
                "2. Check Worker's console shows: '✅ Server started successfully'\n"
                "3. Verify both PCs are on the same network\n"
                "4. Try waiting 10 more seconds and retry\n\n"
                "Check console output for detailed error messages."
            )
            QtWidgets.QMessageBox.critical(self, "Connection Failed", error_msg)
            self.resource_display.setPlainText("❌ Connection failed. See error message.")
        else:
            QtWidgets.QMessageBox.information(self, "Connected", f"✅ Connected to {worker_id}")

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
        if not sel:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a worker to disconnect")
            return

        ip_port = sel.text()

        worker_id = None
        for wid, info in self.network.get_connected_workers().items():
            if f"{info['ip']}:{info['port']}" == ip_port:
                worker_id = wid
                break
        
        if not worker_id:
            QtWidgets.QMessageBox.warning(self, "Worker Not Found", 
                f"Could not find worker {ip_port}")
            return

        reply = QtWidgets.QMessageBox.question(
            self, 
            "Confirm Disconnect",
            f"Disconnect from worker {ip_port}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:

            self.network.disconnect_worker(worker_id)
            print(f"[MASTER] 🔌 Disconnected from worker: {ip_port}")

            with self.worker_resources_lock:
                self.worker_resources.pop(worker_id, None)

            self.refresh_workers_async()
            self.refresh_discovered_workers()
            self.update_resource_display()

            QtWidgets.QMessageBox.information(self, "Disconnected", 
                f"Successfully disconnected from {ip_port}")

            self.disconnect_btn.setEnabled(False)

    def on_task_type_changed(self):
        """Update template dropdown based on selected task type"""
        selected_type_name = self.task_type_combo.currentText()
        try:
            selected_type = TaskType[selected_type_name]
        except KeyError:
            return

        self.template_combo.clear()
        for template_key, template_data in TASK_TEMPLATES.items():
            if template_data.get("type") == selected_type:
                self.template_combo.addItem(template_key)

        if self.template_combo.count() == 0:
            self.template_combo.addItem("Custom")

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

        connected_workers = self.network.get_connected_workers()
        if not connected_workers:
            QtWidgets.QMessageBox.warning(self, "No Workers", "Connect at least one worker before submitting tasks.")
            return

        task_id = self.task_manager.create_task(selected_type, code, data)
        print(f"[MASTER] 📤 Task submitted: {task_id[:8]}... Type: {selected_type.name}")
        print(f"[MASTER] 🔄 Available workers: {len(connected_workers)}")
        print(f"[MASTER] ⚠️  MASTER WILL NOT EXECUTE - Only dispatching to worker")
        
        assigned_worker = self.dispatch_task_to_worker(task_id, code, data)
        if not assigned_worker:
            QtWidgets.QMessageBox.critical(self, "Dispatch Failed", "Failed to dispatch task to any worker.")
            print(f"[MASTER] ❌ Task {task_id[:8]}... dispatch failed - no available workers")
        else:
            worker_short = assigned_worker[:20] + "..." if len(assigned_worker) > 20 else assigned_worker
            print(f"[MASTER] ✅ Task {task_id[:8]}... dispatched to worker {worker_short}")
            print(f"[MASTER] ⏳ Waiting for worker '{worker_short}' to execute and return results...")
        self.refresh_task_table_async()

    def dispatch_task_to_worker(self, task_id: str, code: str, data: dict) -> Optional[str]:
        """Dispatch task to best available worker. Returns worker_id if successful, None otherwise."""
        workers = self.network.get_connected_workers()
        if not workers:
            return None

        target_worker = self._select_worker(workers)
        if not target_worker:
            return None

        task = self.task_manager.get_task(task_id)
        task_name = task.type.name if task else "Unknown Task"
        
        payload = {
            'task_id': task_id,
            'code': code,
            'data': data,
            'name': task_name  # Include task type name for better logging
        }
        sent = self.network.send_task_to_worker(target_worker, payload)
        if sent:
            self.task_manager.assign_task_to_worker(task_id, target_worker)
            return target_worker
        return None

    def _select_worker(self, workers: dict) -> str:
        """Intelligently select the best worker based on available resources and load"""
        resources = self._get_worker_resources_snapshot()
        
        if not resources:

            return list(workers.keys())[0] if workers else None
        
        best_worker = None
        best_score = -1
        
        print(f"[MASTER] 🎯 Load Balancing - Evaluating {len(workers)} workers")
        
        for worker_id in workers.keys():
            stats = resources.get(worker_id, {})

            cpu_available = 100 - stats.get('cpu_percent', 100)  # Available CPU %
            mem_available = stats.get('memory_available_mb', 0) or 0  # Available memory MB
            disk_free = stats.get('disk_free_gb', 0) or 0  # Free disk GB

            active_tasks = 0
            for task_id, task in self.task_manager.tasks.items():
                if task.worker_id == worker_id and task.status.value in ['pending', 'running']:
                    active_tasks += 1

            cpu_score = cpu_available * 0.3
            mem_score = min(mem_available / 1024, 100) * 0.4  # Normalize to 0-100 scale
            task_score = max(0, 100 - (active_tasks * 20)) * 0.2  # Penalty for each task
            disk_score = min(disk_free * 10, 100) * 0.1  # Normalize to 0-100 scale
            
            total_score = cpu_score + mem_score + task_score + disk_score
            
            print(f"[MASTER]   Worker {worker_id[:15]}... Score: {total_score:.1f} "
                  f"(CPU: {cpu_available:.0f}%, Mem: {mem_available:.0f}MB, "
                  f"Tasks: {active_tasks}, Disk: {disk_free:.1f}GB)")
            
            if total_score > best_score:
                best_score = total_score
                best_worker = worker_id
        
        if best_worker:
            print(f"[MASTER] ✅ Selected worker: {best_worker[:15]}... (score: {best_score:.1f})")
        else:

            best_worker = list(workers.keys())[0] if workers else None
            print(f"[MASTER] ⚠️ Using fallback worker selection: {best_worker[:15] if best_worker else 'None'}...")
        
        return best_worker

    def refresh_task_table(self):
        tasks = sorted(self.task_manager.get_all_tasks(), key=lambda t: t.created_at, reverse=True)
        self.tasks_table.setRowCount(len(tasks))
        for row, t in enumerate(tasks):

            id_item = QtWidgets.QTableWidgetItem(t.id[:8])
            self.tasks_table.setItem(row, 0, id_item)

            type_item = QtWidgets.QTableWidgetItem(t.type.name)
            self.tasks_table.setItem(row, 1, type_item)

            status_item = QtWidgets.QTableWidgetItem(t.status.name)
            self.tasks_table.setItem(row, 2, status_item)

            worker_text = ""
            if t.worker_id:
                worker_text = t.worker_id.split(":")[0] if ":" in t.worker_id else t.worker_id
            worker_item = QtWidgets.QTableWidgetItem(worker_text)
            self.tasks_table.setItem(row, 3, worker_item)

            progress_widget = QtWidgets.QProgressBar()
            try:
                prog_val = int(getattr(t, 'progress', 0) or 0)
            except Exception:
                prog_val = 0
            progress_widget.setRange(0, 100)
            progress_widget.setValue(max(0, min(100, prog_val)))
            progress_widget.setTextVisible(True)
            progress_widget.setFormat(f"{progress_widget.value()}%")
            progress_widget.setAlignment(QtCore.Qt.AlignCenter)
            self.tasks_table.setCellWidget(row, 4, progress_widget)

            result_text = ""
            if t.result is not None:
                if isinstance(t.result, dict):

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

            output_text = ""
            if hasattr(t, 'output') and t.output:
                output_text = str(t.output)
            elif t.error:
                output_text = f"ERROR:\n{t.error}"
            elif t.result is not None:

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

            output_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.tasks_table.setItem(row, 6, output_item)

            status_item = self.tasks_table.item(row, 2)
            if status_item:
                st = status_item.text().upper()
                try:
                    if st.startswith('COMPLETED') or 'SUCCESS' in st:
                        color = QtGui.QColor(200, 255, 200)
                    elif st.startswith('RUNNING') or st.startswith('IN_PROGRESS'):
                        color = QtGui.QColor(255, 250, 200)
                    elif st.startswith('FAILED') or 'ERROR' in st or st.startswith('CANCEL'):
                        color = QtGui.QColor(255, 200, 200)
                    else:
                        color = QtGui.QColor(230, 230, 250)
                    status_item.setBackground(QtGui.QBrush(color))
                except Exception:
                    pass

            lines = output_text.count('\n') + 1
            estimated = max(40, min(300, lines * 18))
            self.tasks_table.setRowHeight(row, estimated)

    def refresh_task_table_async(self):
        QtCore.QTimer.singleShot(0, self.refresh_task_table)

    def handle_progress_update(self, worker_id, data):
        task_id = data.get("task_id")
        progress = data.get("progress", 0)

        if progress in [0, 25, 50, 75, 100]:
            print(f"[MASTER] ⏳ Task {task_id[:8] if task_id else 'unknown'}... progress: {progress}%")
        self.task_manager.update_task_progress(task_id, progress)
        self.refresh_task_table_async()

    def handle_task_result(self, worker_id, data):
        task_id = data.get("task_id")
        result_payload = data.get("result", {})
        
        worker_short = worker_id[:20] + "..." if len(worker_id) > 20 else worker_id
        print(f"[MASTER] 📥 Received result from worker {worker_short}")
        print(f"[MASTER] 📊 VERIFICATION: Task {task_id[:8] if task_id else 'unknown'}... was executed on worker, NOT on master")

        if result_payload.get("success"):
            print(f"[MASTER] ✅ Task {task_id[:8] if task_id else 'unknown'}... completed successfully")
        else:
            error = result_payload.get("error", "Unknown error")
            print(f"[MASTER] ❌ Task {task_id[:8] if task_id else 'unknown'}... failed: {error[:50]}")

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
        with self.worker_resources_lock:
            self.worker_resources[worker_id] = data.copy()

        QtCore.QTimer.singleShot(0, self.update_resource_display)
    
    def update_resource_display(self):
        """Update the resource display with current worker data"""

        snapshot = self._get_worker_resources_snapshot()

        if not snapshot:
            connected_workers = self.network.get_connected_workers()
            if not connected_workers:
                self.resource_display.setPlainText(
                    "⏳ Waiting for worker resources...\n\nConnect a worker and resources will appear here."
                )
            else:
                self.resource_display.setPlainText(
                    f"✅ Connected to {len(connected_workers)} worker(s)\n\n⏳ Loading resource data..."
                )
            return

        output = []
        output.append(f"📊 LIVE WORKER RESOURCES - {len(snapshot)} Connected")
        output.append(f"🕐 Updated: {time.strftime('%H:%M:%S')}")
        output.append("=" * 50)
        output.append("")
        
        for wid, stats in snapshot.items():

            worker_ip = wid.split(":")[0] if ":" in wid else wid

            cpu = stats.get("cpu_percent", 0.0)
            mem_percent = stats.get("memory_percent", 0.0)
            mem_total_mb = stats.get("memory_total_mb", 0.0)
            mem_avail_mb = stats.get("memory_available_mb", 0.0)
            mem_used_mb = mem_total_mb - mem_avail_mb if mem_total_mb > 0 else 0
            disk_percent = stats.get("disk_percent", 0.0)
            disk_free_gb = stats.get("disk_free_gb", 0.0)
            battery = stats.get("battery_percent")
            plugged = stats.get("battery_plugged")

            def status(val):
                return "🟢" if val < 50 else "🟡" if val < 75 else "🔴"
            
            output.append(f"🖥️  WORKER: {worker_ip}")
            output.append("-" * 50)

            output.append(f"{status(cpu)} CPU Usage:          {cpu:5.1f}%")

            mem_total_gb = mem_total_mb / 1024
            mem_used_gb = mem_used_mb / 1024
            mem_avail_gb = mem_avail_mb / 1024
            output.append(f"{status(mem_percent)} Memory Usage:       {mem_percent:5.1f}%")
            output.append(f"   • Total RAM:        {mem_total_gb:6.2f} GB")
            output.append(f"   • Used RAM:         {mem_used_gb:6.2f} GB")
            output.append(f"   💚 UNUTILIZED RAM:  {mem_avail_gb:6.2f} GB ⭐")

            output.append(f"{status(disk_percent)} Disk Usage:         {disk_percent:5.1f}%")
            output.append(f"   • Free Space:       {disk_free_gb:6.1f} GB")

            if battery is not None:
                icon = "🔌" if plugged else "🔋"
                status_text = "Charging" if plugged else "On Battery"
                output.append(f"{icon} Battery:            {battery:5.0f}% ({status_text})")
            else:
                output.append("⚡ Power:              AC (No Battery)")
            
            output.append("")
        
        final_text = "\n".join(output)

        self.resource_display.setPlainText(final_text)

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

            if hasattr(self, 'discovery_timer'):
                self.discovery_timer.stop()

            time.sleep(0.1)
            self.network.stop()
        except Exception as ex:
            print(f"Error during cleanup: {ex}")
        finally:
            super().closeEvent(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MasterUI()
    sys.exit(app.exec_())
