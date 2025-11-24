"""
WinLink Enhanced UI Demo Launcher
Showcases the improved modern interface with animations and effects
"""

import sys
import argparse
from PyQt5.QtWidgets import (
    QApplication, QSplashScreen, QProgressBar, QVBoxLayout, QLabel,
    QWidget, QSystemTrayIcon
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

from main import WelcomeScreen
from role_select import RoleSelectScreen
from master.master_ui import MasterUI
from worker.worker_ui import WorkerUI
from ui.modern_components import ModernNotification, ModernSystemTray
from assets.styles import STYLE_SHEET


class InitializationThread(QThread):
    """Background thread for app initialization"""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def run(self):
        import time
        steps = [
            (20, "Initializing core modules..."),
            (40, "Loading network components..."),
            (60, "Setting up UI components..."),
            (80, "Applying modern theme..."),
            (100, "Ready to launch!")
        ]
        for progress, message in steps:
            self.progress_updated.emit(progress, message)
            time.sleep(0.5)
        self.finished.emit()


class ModernSplashScreen(QSplashScreen):
    """Modern splash screen with loading animation"""
    
    def __init__(self):
        # Create pixmap
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor(26, 26, 58))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        from PyQt5.QtGui import QLinearGradient
        grad = QLinearGradient(0, 0, 500, 300)
        grad.setColorAt(0, QColor(52, 73, 94))
        grad.setColorAt(0.5, QColor(44, 62, 80))
        grad.setColorAt(1, QColor(34, 49, 63))
        painter.fillRect(pixmap.rect(), grad)
        painter.setPen(QColor(255,255,255))
        painter.setFont(QFont("Arial", 32, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "WinLink")
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Progress UI
        self._setup_progress_bar()
        
        # Thread
        self.init_thread = InitializationThread()
        self.init_thread.progress_updated.connect(self._update_progress)
        self.init_thread.finished.connect(self._launch_main_app)

    def _setup_progress_bar(self):
        pw = QWidget(self)
        pw.setGeometry(50, 220, 400, 60)
        l = QVBoxLayout(pw)
        l.setSpacing(10)
        self.progress_label = QLabel("Initializing WinLink...")
        self.progress_label.setStyleSheet("color:white; font-size:14px;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border:2px solid rgba(255,255,255,0.3);
                border-radius:8px;
                background:rgba(255,255,255,0.1);
                text-align:center;
                color:white;
                height:20px;
            }
            QProgressBar::chunk {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                           stop:0 #00d4aa,
                                           stop:1 #00ff88);
                border-radius:6px;
            }
        """)
        self.progress_bar.setValue(0)
        l.addWidget(self.progress_label)
        l.addWidget(self.progress_bar)

    def start_loading(self):
        self.show()
        self.init_thread.start()

    def _update_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.progress_label.setText(msg)

    def _launch_main_app(self):
        QTimer.singleShot(500, self._finish_and_launch)

    def _finish_and_launch(self):
        self.close()
        # Keep a reference so Python doesn't GC it
        self.main_window = WelcomeScreen()
        self.main_window.show()


def create_system_tray(app):
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = ModernSystemTray()
        tray.show()
        QTimer.singleShot(1000, lambda: tray.show_notification(
            "WinLink Started",
            "Distributed computing platform is ready!",
            "🚀"
        ))
        return tray
    return None


def main():
    parser = argparse.ArgumentParser(description='WinLink Enhanced UI Demo')
    parser.add_argument('--skip-splash', action='store_true')
    parser.add_argument('--direct', choices=['master','worker','select'])
    parser.add_argument('--no-tray', action='store_true')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("WinLink Enhanced")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("WinLink FYP")
    app.setStyleSheet(STYLE_SHEET)
    
    # System tray
    tray = None
    if not args.no_tray:
        tray = create_system_tray(app)
    
    # Direct launches
    if args.direct == 'master':
        window = MasterUI(); window.show()
    elif args.direct == 'worker':
        window = WorkerUI();  window.show()
    elif args.direct == 'select':
        window = RoleSelectScreen(); window.show()
    else:
        if args.skip_splash:
            window = WelcomeScreen(); window.show()
        else:
            splash = ModernSplashScreen()
            splash.start_loading()
    
    # Demo notification
    QTimer.singleShot(3000, lambda: ModernNotification(
        "Welcome to WinLink Enhanced!",
        "Experience the new modern interface.",
        "🎨", duration=5000
    ))
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
