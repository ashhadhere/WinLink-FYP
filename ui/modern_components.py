"""
Modern UI Components for WinLink
Includes notifications, system tray, and enhanced widgets
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                            QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect,
                            QGraphicsOpacityEffect, QApplication, QDesktopWidget, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush

class ModernNotification(QWidget):
    """Modern notification widget with smoother UI and animations"""

    def __init__(self, title, message, icon="ℹ️", duration=4000, parent=None):
        super().__init__(parent)
        self.duration = duration
        self.setup_ui(title, message, icon)
        self.setup_animations()
        self.show_notification()

    def setup_ui(self, title, message, icon):
        self.setFixedSize(350, 100)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main container
        container = QFrame(self)
        container.setGeometry(0, 0, 350, 100)
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 44, 52, 0.85);  /* dark translucent background */
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 16px;
            }
        """)

        # Drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        container.setGraphicsEffect(shadow)

        layout = QHBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(16, 12, 16, 12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: white;
            }
        """)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #00d4aa;
                font-size: 15px;
                font-weight: bold;
                margin: 0;
            }
        """)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
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
        # Slide in animation
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(400)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Fade out animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InCubic)

    def show_notification(self):
        # Position at bottom right of screen
        screen = QApplication.primaryScreen().availableGeometry()
        start_pos = QRect(screen.width(), screen.height() - 120, 350, 100)
        end_pos = QRect(screen.width() - 370, screen.height() - 120, 350, 100)

        self.setGeometry(start_pos)
        self.show()

        # Slide in
        self.slide_animation.setStartValue(start_pos)
        self.slide_animation.setEndValue(end_pos)
        self.slide_animation.start()

        # Auto close after duration
        QTimer.singleShot(self.duration, self.close_notification)

    def close_notification(self):
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()


class ModernSystemTray(QSystemTrayIcon):
    """Enhanced system tray with modern context menu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_tray()
        self.setup_menu()

    def setup_tray(self):
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "WinLink_logo.ico")
        
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 212, 170))
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(painter.font())
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "W")
            painter.end()
            
            self.setIcon(QIcon(pixmap))
        
        self.setToolTip("WinLink - Distributed Computing Platform")

    def setup_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(26, 26, 58, 0.95);
                border: 2px solid rgba(0, 212, 170, 0.3);
                border-radius: 8px;
                color: white;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 212, 170, 0.3);
            }
        """)
        
        # Actions
        show_action = QAction("Show WinLink", self)
        show_action.triggered.connect(self.show_main_window)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        
        menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.quit)
        
        menu.addAction(show_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)

    def show_main_window(self):
        # Signal to show main window
        if self.parent():
            self.parent().show()
            self.parent().raise_()
            self.parent().activateWindow()

    def show_settings(self):
        # Placeholder for settings dialog
        self.show_notification("Settings", "Settings dialog coming soon!", "⚙️")

    def show_notification(self, title, message, icon="ℹ️"):
        """Show a modern notification"""
        notification = ModernNotification(title, message, icon)

class StatusIndicator(QLabel):
    """Animated status indicator with color coding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.status = "offline"
        self.setup_animation()
        self.update_status("offline")

    def setup_animation(self):
        self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.3)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop
        self.pulse_animation.setDirection(QPropertyAnimation.Backward)

    def update_status(self, status):
        self.status = status
        if status == "online":
            self.setStyleSheet("""
                QLabel {
                    background-color: #00c853;
                    border: 2px solid #00ff88;
                    border-radius: 6px;
                }
            """)
            self.pulse_animation.stop()
            self.setWindowOpacity(1.0)
        elif status == "connecting":
            self.setStyleSheet("""
                QLabel {
                    background-color: #ff9800;
                    border: 2px solid #ffcc02;
                    border-radius: 6px;
                }
            """)
            self.pulse_animation.start()
        else:  # offline
            self.setStyleSheet("""
                QLabel {
                    background-color: #f44336;
                    border: 2px solid #ff6659;
                    border-radius: 6px;
                }
            """)
            self.pulse_animation.stop()
            self.setWindowOpacity(1.0)

class ModernCard(QFrame):
    """Reusable modern card component with hover effects and clean UI"""

    clicked = pyqtSignal()

    def __init__(self, title="", content="", icon="", parent=None):
        super().__init__(parent)
        self.setup_ui(title, content, icon)
        self.setup_effects()

    def setup_ui(self, title, content, icon):
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.07);  /* translucent white */
                border-radius: 16px;
                border: none;  /* removes ugly border */
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        if icon:
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("font-size: 32px; margin: 10px;")
            layout.addWidget(icon_label)

        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 18px;
                    font-weight: 600;
                }
            """)
            layout.addWidget(title_label)

        if content:
            content_label = QLabel(content)
            content_label.setAlignment(Qt.AlignCenter)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("""
                QLabel {
                    color: rgba(255,255,255,0.8);
                    font-size: 14px;
                }
            """)
            layout.addWidget(content_label)

    def setup_effects(self):
        # Drop shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 5)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self.shadow)

        # Hover animation for blur
        self.hover_animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self.hover_animation.setDuration(200)

    def enterEvent(self, event):
        self.hover_animation.setStartValue(15)
        self.hover_animation.setEndValue(25)
        self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_animation.setStartValue(25)
        self.hover_animation.setEndValue(15)
        self.hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
