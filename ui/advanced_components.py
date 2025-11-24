"""
Advanced UI Components for WinLink
Ultra-modern components with enhanced animations and styling
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                            QProgressBar, QPushButton, QGraphicsDropShadowEffect,
                            QGraphicsOpacityEffect, QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont

class ModernCard(QFrame):
    """Enhanced card widget with hover animations and glow effects"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title="", description="", icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.icon = icon
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        self.setObjectName("modernCard")
        self.setFixedSize(280, 160)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply enhanced shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 8)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 32px;
                    color: #00f5a0;
                    margin-bottom: 8px;
                }
            """)
            layout.addWidget(icon_label)
        
        # Title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: 700;
                    margin-bottom: 4px;
                }
            """)
            layout.addWidget(title_label)
        
        # Description
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #c1d5e0;
                    font-size: 12px;
                    font-weight: 400;
                    line-height: 1.4;
                }
            """)
            layout.addWidget(desc_label)

    def setup_animations(self):
        # Hover scale animation
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Shadow animation
        self.shadow_animation = QPropertyAnimation(self.shadow, b"offset")
        self.shadow_animation.setDuration(200)
        self.shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        # Scale up and enhance shadow on hover
        current_geometry = self.geometry()
        center = current_geometry.center()
        new_size = QRect(0, 0, 290, 170)
        new_size.moveCenter(center)
        
        self.scale_animation.setStartValue(current_geometry)
        self.scale_animation.setEndValue(new_size)
        self.scale_animation.start()
        
        self.shadow.setBlurRadius(40)
        self.shadow.setOffset(0, 12)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Scale back down
        current_geometry = self.geometry()
        center = current_geometry.center()
        new_size = QRect(0, 0, 280, 160)
        new_size.moveCenter(center)
        
        self.scale_animation.setStartValue(current_geometry)
        self.scale_animation.setEndValue(new_size)
        self.scale_animation.start()
        
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 8)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class AnimatedProgressBar(QProgressBar):
    """Progress bar with smooth animations and glow effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        self.setTextVisible(True)
        self.setRange(0, 100)
        self.setValue(0)
        
        # Apply glow effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(20)
        self.glow.setOffset(0, 0)
        self.glow.setColor(QColor(0, 245, 160, 150))
        self.setGraphicsEffect(self.glow)

    def setup_animations(self):
        self.value_animation = QPropertyAnimation(self, b"value")
        self.value_animation.setDuration(800)
        self.value_animation.setEasingCurve(QEasingCurve.OutQuad)

    def setAnimatedValue(self, value):
        """Set value with smooth animation"""
        self.value_animation.setStartValue(self.value())
        self.value_animation.setEndValue(value)
        self.value_animation.start()


class StatusIndicator(QLabel):
    """Animated status indicator with color-coded states"""
    
    def __init__(self, status="offline", parent=None):
        super().__init__(parent)
        self.current_status = status
        self.setup_ui()
        self.setup_animations()
        self.update_status(status)

    def setup_ui(self):
        self.setFixedSize(16, 16)
        self.setAlignment(Qt.AlignCenter)
        self.setText("●")
        self.setStyleSheet("font-size: 16px; font-weight: bold;")

    def setup_animations(self):
        # Pulsing animation for online status
        self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(0.6)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutSine)

    def update_status(self, status):
        """Update status with color and animation"""
        self.current_status = status
        
        if status == "online":
            self.setStyleSheet("color: #00f5a0; font-size: 16px; font-weight: bold;")
            self.pulse_animation.start()
        elif status == "offline":
            self.setStyleSheet("color: #ff6b6b; font-size: 16px; font-weight: bold;")
            self.pulse_animation.stop()
            self.setWindowOpacity(1.0)
        elif status == "warning":
            self.setStyleSheet("color: #ffd93d; font-size: 16px; font-weight: bold;")
            self.pulse_animation.stop()
            self.setWindowOpacity(1.0)
        elif status == "processing":
            self.setStyleSheet("color: #667eea; font-size: 16px; font-weight: bold;")
            self.pulse_animation.start()


class ModernButton(QPushButton):
    """Enhanced button with advanced hover effects and animations"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        self.setMinimumSize(120, 45)
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        
        # Apply shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        
        self.update_style()

    def update_style(self):
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #00f5a0, stop:1 #00d4aa);
                    color: #000000;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #00ff88, stop:1 #00f5a0);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #00d4aa, stop:1 #00c851);
                }
            """)
        elif self.button_type == "danger":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #ff6b6b, stop:1 #ee5a52);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #ff8a80, stop:1 #ff6b6b);
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.1);
                    color: #e8f4fd;
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 12px;
                    font-weight: 600;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.15);
                    border: 1px solid rgba(0, 245, 160, 0.5);
                }
            """)

    def setup_animations(self):
        # Scale animation
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        # Enhanced shadow on hover
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 6)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Reset shadow
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        super().leaveEvent(event)


class LoadingSpinner(QLabel):
    """Modern loading spinner with smooth rotation"""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.size = size
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        self.setFixedSize(self.size, self.size)
        self.setText("⚙️")  # Using gear emoji as spinner
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                font-size: {self.size - 8}px;
                color: #00f5a0;
            }}
        """)

    def setup_animations(self):
        self.rotation_animation = QPropertyAnimation(self, b"rotation")
        self.rotation_animation.setDuration(1000)
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(360)
        self.rotation_animation.setLoopCount(-1)  # Infinite loop
        self.rotation_animation.setEasingCurve(QEasingCurve.Linear)

    def start_spinning(self):
        """Start the loading animation"""
        self.show()
        self.rotation_animation.start()

    def stop_spinning(self):
        """Stop the loading animation"""
        self.rotation_animation.stop()
        self.hide()


class MetricCard(QFrame):
    """Metric display card with animated value updates"""
    
    def __init__(self, title="", value="0", unit="", icon="📊", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_value = value
        self.unit = unit
        self.icon = icon
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("modernCard")
        self.setFixedSize(200, 120)
        
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
        icon_label.setStyleSheet("font-size: 20px;")
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #c1d5e0;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value display
        self.value_label = QLabel(f"{self.current_value}{self.unit}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 700;
                margin: 8px 0;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def update_value(self, new_value):
        """Update the displayed value with animation"""
        self.current_value = new_value
        self.value_label.setText(f"{new_value}{self.unit}")
        
        # Add a subtle scale animation
        self.value_label.setStyleSheet("""
            QLabel {
                color: #00f5a0;
                font-size: 26px;
                font-weight: 700;
                margin: 8px 0;
            }
        """)
        
        # Reset style after a short delay
        QTimer.singleShot(300, lambda: self.value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 700;
                margin: 8px 0;
            }
        """))


class ModernToast(QWidget):
    """Modern toast notification with slide-in animation"""
    
    def __init__(self, title, message, toast_type="info", duration=3000, parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.setup_ui()
        self.setup_animations()
        self.show_toast()

    def setup_ui(self):
        self.setFixedSize(400, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Position at top-right of screen
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - 420, 20)
        
        # Main container
        container = QFrame(self)
        container.setGeometry(0, 0, 400, 80)
        
        # Style based on type
        if self.toast_type == "success":
            color_start = "rgba(0, 245, 160, 0.95)"
            color_end = "rgba(0, 212, 170, 0.95)"
            border_color = "rgba(0, 245, 160, 1)"
        elif self.toast_type == "error":
            color_start = "rgba(255, 107, 107, 0.95)"
            color_end = "rgba(238, 90, 82, 0.95)"
            border_color = "rgba(255, 107, 107, 1)"
        elif self.toast_type == "warning":
            color_start = "rgba(255, 217, 61, 0.95)"
            color_end = "rgba(255, 193, 7, 0.95)"
            border_color = "rgba(255, 217, 61, 1)"
        else:  # info
            color_start = "rgba(102, 126, 234, 0.95)"
            color_end = "rgba(118, 75, 162, 0.95)"
            border_color = "rgba(102, 126, 234, 1)"
        
        container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 {color_start},
                                           stop:1 {color_end});
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        # Apply shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        container.setGraphicsEffect(shadow)
        
        # Layout
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        
        # Icon based on type
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon_label = QLabel(icons.get(self.toast_type, "ℹ️"))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 18px;")
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 700;
                margin: 0;
            }
        """)
        
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.9);
                font-size: 13px;
                font-weight: 400;
                margin: 0;
            }
        """)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)

    def setup_animations(self):
        # Slide in from right
        self.slide_in = QPropertyAnimation(self, b"pos")
        self.slide_in.setDuration(400)
        self.slide_in.setEasingCurve(QEasingCurve.OutCubic)
        
        # Slide out to right
        self.slide_out = QPropertyAnimation(self, b"pos")
        self.slide_out.setDuration(300)
        self.slide_out.setEasingCurve(QEasingCurve.InCubic)
        
        # Fade out
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)

    def show_toast(self):
        """Show the toast with animation"""
        screen = QApplication.desktop().screenGeometry()
        start_pos = screen.width(), 20
        end_pos = screen.width() - 420, 20
        
        self.move(*start_pos)
        self.show()
        
        self.slide_in.setStartValue(start_pos)
        self.slide_in.setEndValue(end_pos)
        self.slide_in.start()
        
        # Auto-hide after duration
        QTimer.singleShot(self.duration, self.hide_toast)

    def hide_toast(self):
        """Hide the toast with animation"""
        screen = QApplication.desktop().screenGeometry()
        start_pos = self.pos()
        end_pos = screen.width(), start_pos.y()
        
        self.slide_out.setStartValue(start_pos)
        self.slide_out.setEndValue(end_pos)
        self.slide_out.finished.connect(self.close)
        self.slide_out.start()
