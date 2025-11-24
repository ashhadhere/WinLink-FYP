"""
Enhanced Dashboard Components for WinLink Master UI
Modern data visualization and monitoring widgets
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                            QProgressBar, QScrollArea, QListWidget, QListWidgetItem,
                            QGraphicsDropShadowEffect, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush
import json
from datetime import datetime

class ModernDashboard(QFrame):
    """Enhanced dashboard with modern metrics and visualizations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("glass", True)
        self.setup_ui()
        self.setup_update_timer()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Dashboard header
        header = QLabel("📊 System Dashboard")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)

        # Create metric cards
        self.active_workers_card = MetricCard("Active Workers", "0", "", "👥")
        self.completed_tasks_card = MetricCard("Completed Tasks", "0", "", "✅")
        self.pending_tasks_card = MetricCard("Pending Tasks", "0", "", "⏳")
        self.total_cpu_card = MetricCard("Total CPU Usage", "0", "%", "🖥️")

        metrics_grid.addWidget(self.active_workers_card, 0, 0)
        metrics_grid.addWidget(self.completed_tasks_card, 0, 1)
        metrics_grid.addWidget(self.pending_tasks_card, 1, 0)
        metrics_grid.addWidget(self.total_cpu_card, 1, 1)

        layout.addLayout(metrics_grid)

        # Activity timeline
        timeline_label = QLabel("📈 Recent Activity")
        timeline_label.setObjectName("subHeaderLabel")
        layout.addWidget(timeline_label)

        self.activity_timeline = ActivityTimeline()
        layout.addWidget(self.activity_timeline)

    def setup_update_timer(self):
        """Setup timer for regular dashboard updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(3000)  # Update every 3 seconds

    def update_metrics(self):
        """Update dashboard metrics with animated values"""
        import random
        
        # Simulate metric updates
        self.active_workers_card.update_value(random.randint(1, 5))
        self.completed_tasks_card.update_value(random.randint(10, 50))
        self.pending_tasks_card.update_value(random.randint(0, 8))
        self.total_cpu_card.update_value(random.randint(20, 80))

    def add_activity(self, activity_type, message):
        """Add new activity to timeline"""
        self.activity_timeline.add_activity(activity_type, message)


class MetricCard(QFrame):
    """Enhanced metric display card with animations"""
    
    value_changed = pyqtSignal(str)
    
    def __init__(self, title="", value="0", unit="", icon="📊", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_value = value
        self.unit = unit
        self.icon = icon
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(220, 140)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 rgba(255,255,255,0.12),
                                           stop:1 rgba(255,255,255,0.08));
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 16px;
                padding: 16px;
            }
        """)
        
        # Apply shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                margin-right: 8px;
            }
        """)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value display with enhanced styling
        self.value_label = QLabel(f"{self.current_value}{self.unit}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: 700;
                margin: 12px 0;
                text-shadow: 0px 2px 8px rgba(0,0,0,0.3);
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def update_value(self, new_value):
        """Update the displayed value with animation effect"""
        self.current_value = new_value
        self.value_label.setText(f"{new_value}{self.unit}")
        
        # Add highlight animation
        self.value_label.setStyleSheet("""
            QLabel {
                color: #00f5a0;
                font-size: 34px;
                font-weight: 700;
                margin: 12px 0;
                text-shadow: 0px 0px 15px rgba(0, 245, 160, 0.6);
            }
        """)
        
        # Reset style after animation
        QTimer.singleShot(500, self.reset_value_style)
        
        self.value_changed.emit(str(new_value))

    def reset_value_style(self):
        """Reset value label to normal style"""
        self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: 700;
                margin: 12px 0;
                text-shadow: 0px 2px 8px rgba(0,0,0,0.3);
            }
        """)


class ActivityTimeline(QScrollArea):
    """Modern activity timeline with animated entries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.activities = []

    def setup_ui(self):
        self.setFixedHeight(200)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.setWidget(self.container)
        
        # Styling
        self.setStyleSheet("""
            QScrollArea {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
            }
        """)

    def add_activity(self, activity_type, message):
        """Add new activity with animation"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create activity widget
        activity_widget = ActivityItem(activity_type, message, timestamp)
        
        # Insert at top
        self.layout.insertWidget(0, activity_widget)
        self.activities.insert(0, activity_widget)
        
        # Limit to 10 activities
        if len(self.activities) > 10:
            old_activity = self.activities.pop()
            old_activity.deleteLater()
        
        # Scroll to top
        self.verticalScrollBar().setValue(0)


class ActivityItem(QFrame):
    """Individual activity item with modern styling"""
    
    def __init__(self, activity_type, message, timestamp, parent=None):
        super().__init__(parent)
        self.activity_type = activity_type
        self.message = message
        self.timestamp = timestamp
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(0, 245, 160, 0.3);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Activity type icon
        icon_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "task": "⚙️",
            "worker": "👤"
        }
        
        icon_label = QLabel(icon_map.get(self.activity_type, "📋"))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 16px;")
        
        # Message content
        message_layout = QVBoxLayout()
        message_layout.setSpacing(2)
        
        message_label = QLabel(self.message)
        message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 11px;
                font-weight: 400;
            }
        """)
        
        message_layout.addWidget(message_label)
        message_layout.addWidget(time_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(message_layout)
        layout.addStretch()


class WorkerStatusPanel(QFrame):
    """Enhanced worker status panel with real-time updates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("glass", True)
        self.workers = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("🖥️ Worker Network Status")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Workers container
        self.workers_scroll = QScrollArea()
        self.workers_scroll.setWidgetResizable(True)
        self.workers_scroll.setFixedHeight(300)
        self.workers_scroll.setStyleSheet("""
            QScrollArea {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
            }
        """)

        self.workers_container = QWidget()
        self.workers_layout = QVBoxLayout(self.workers_container)
        self.workers_layout.setSpacing(8)
        self.workers_layout.setContentsMargins(10, 10, 10, 10)
        
        self.workers_scroll.setWidget(self.workers_container)
        layout.addWidget(self.workers_scroll)

    def add_worker(self, worker_id, worker_info):
        """Add new worker to the panel"""
        worker_widget = WorkerCard(worker_id, worker_info)
        self.workers_layout.addWidget(worker_widget)
        self.workers[worker_id] = worker_widget

    def update_worker(self, worker_id, worker_info):
        """Update existing worker information"""
        if worker_id in self.workers:
            self.workers[worker_id].update_info(worker_info)

    def remove_worker(self, worker_id):
        """Remove worker from panel"""
        if worker_id in self.workers:
            self.workers[worker_id].deleteLater()
            del self.workers[worker_id]


class WorkerCard(QFrame):
    """Individual worker status card"""
    
    def __init__(self, worker_id, worker_info, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self.worker_info = worker_info
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 12px;
                margin: 4px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(15)
        
        # Worker icon and status
        status_layout = QVBoxLayout()
        
        worker_icon = QLabel("🖥️")
        worker_icon.setAlignment(Qt.AlignCenter)
        worker_icon.setStyleSheet("font-size: 24px;")
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #00f5a0;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(worker_icon)
        status_layout.addWidget(self.status_indicator)
        
        # Worker information
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        self.worker_name = QLabel(f"Worker {self.worker_id}")
        self.worker_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
            }
        """)
        
        self.worker_details = QLabel(f"IP: {self.worker_info.get('ip', 'Unknown')}")
        self.worker_details.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 12px;
                font-weight: 400;
            }
        """)
        
        info_layout.addWidget(self.worker_name)
        info_layout.addWidget(self.worker_details)
        
        # Performance metrics
        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(4)
        
        self.cpu_label = QLabel(f"CPU: {self.worker_info.get('cpu', 0)}%")
        self.cpu_label.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        self.memory_label = QLabel(f"Memory: {self.worker_info.get('memory', 0)}%")
        self.memory_label.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        metrics_layout.addWidget(self.cpu_label)
        metrics_layout.addWidget(self.memory_label)
        
        layout.addLayout(status_layout)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addLayout(metrics_layout)

    def update_info(self, worker_info):
        """Update worker information"""
        self.worker_info = worker_info
        self.worker_details.setText(f"IP: {worker_info.get('ip', 'Unknown')}")
        self.cpu_label.setText(f"CPU: {worker_info.get('cpu', 0)}%")
        self.memory_label.setText(f"Memory: {worker_info.get('memory', 0)}%")
        
        # Update status color based on performance
        cpu_usage = worker_info.get('cpu', 0)
        if cpu_usage > 80:
            color = "#ff6b6b"  # Red for high usage
        elif cpu_usage > 50:
            color = "#ffd93d"  # Yellow for medium usage
        else:
            color = "#00f5a0"  # Green for low usage
            
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
