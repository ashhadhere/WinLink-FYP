"""
WinLink Launcher for Windows
Launches the WinLink application with enhanced security features
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QSplashScreen, QProgressBar, QVBoxLayout, QLabel,
    QWidget, QSystemTrayIcon, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import WelcomeScreen
from role_select import RoleSelectScreen
from master.master_ui import MasterUI
from worker.worker_ui import WorkerUI
from assets.styles import STYLE_SHEET

try:
    from ui.modern_components import ModernNotification, ModernSystemTray
except ImportError:
    # Fallback if modern components not available
    ModernNotification = None
    ModernSystemTray = None


class InitializationThread(QThread):
    """Background thread for app initialization"""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def __init__(self, enable_security_checks=True):
        super().__init__()
        self.enable_security_checks = enable_security_checks
    
    def run(self):
        import time
        steps = [
            (10, "Checking prerequisites..."),
            (20, "Initializing core modules..."),
            (30, "Setting up security..."),
            (40, "Loading network components..."),
            (50, "Initializing database..."),
            (60, "Setting up task executor..."),
            (70, "Loading scheduler..."),
            (80, "Setting up UI components..."),
            (90, "Applying security configuration..."),
            (100, "Ready to launch!")
        ]
        
        for progress, message in steps:
            self.progress_updated.emit(progress, message)
            
            # Perform actual initialization steps
            if progress == 10 and self.enable_security_checks:
                self._check_prerequisites()
            elif progress == 30:
                self._setup_security()
            elif progress == 50:
                self._init_database()
            
            time.sleep(0.3)
        
        self.finished.emit()
    
    def _check_prerequisites(self):
        """Check basic prerequisites"""
        try:
            import PyQt5
            import psutil
        except ImportError as e:
            self.progress_updated.emit(10, f"Missing dependency: {e}")
            time.sleep(1)
    
    def _setup_security(self):
        """Setup security components"""
        try:
            # Create necessary directories
            os.makedirs("secrets", exist_ok=True)
            os.makedirs("ssl", exist_ok=True)
            os.makedirs("data", exist_ok=True)
            os.makedirs("logs", exist_ok=True)
        except Exception:
            pass
    
    def _init_database(self):
        """Initialize database"""
        try:
            from core.database import get_database
            db = get_database()
        except Exception:
            pass


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

    def __init__(self, enable_security_checks=False):
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
        self.init_thread = InitializationThread(enable_security_checks)
        self.init_thread.progress_updated.connect(self._update_progress)
        self.init_thread.finished.connect(self._launch_main_app)

    def _launch_main_app(self):
        QTimer.singleShot(500, self._finish_and_launch)

    def _finish_and_launch(self):
        self.close()
        # Keep a reference so Python doesn't GC it
        self.main_window = WelcomeScreen()
        self.main_window.show()


def create_system_tray(app):
    if QSystemTrayIcon.isSystemTrayAvailable():
        if ModernSystemTray:
            tray = ModernSystemTray()
            tray.show()
            QTimer.singleShot(1000, lambda: tray.show_notification(
                "WinLink Started",
                "Secure distributed computing platform is ready!",
                "🔐"
            ))
            return tray
        else:
            # Basic system tray fallback
            from PyQt5.QtGui import QIcon
            tray = QSystemTrayIcon()
            if tray.isSystemTrayAvailable():
                tray.show()
                return tray
    return None


def check_and_setup_security():
    """Check and setup security components"""
    print("🔐 Setting up security components...")
    
    # Create auth token if needed
    token_file = Path("secrets/auth_token.txt")
    if not token_file.exists():
        import secrets
        token = secrets.token_urlsafe(32)
        with open(token_file, 'w') as f:
            f.write(token)
        print("✅ Authentication token created")
    
    # Check certificates
    cert_file = Path("ssl/server.crt")
    key_file = Path("ssl/server.key")
    if not (cert_file.exists() and key_file.exists()):
        print("⚠️  TLS certificates not found")
        print("   Run 'python windows_setup_certificates.py' to generate them")


def main():
    parser = argparse.ArgumentParser(
        description="WinLink Desktop Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_enhanced.py                    # Start with welcome screen
  python launch_enhanced.py --role master     # Start as master node
  python launch_enhanced.py --role worker     # Start as worker node
  python launch_enhanced.py --test           # Run security tests
  python launch_enhanced.py --demo           # Run security demo
        """
    )
    
    parser.add_argument('--role', choices=['master', 'worker'],
                       help='Start in specific role')
    parser.add_argument('--skip-splash', action='store_true',
                       help='Skip splash screen')
    parser.add_argument('--no-tray', action='store_true',
                       help='Disable system tray')
    parser.add_argument('--test', action='store_true',
                       help='Run security tests')
    parser.add_argument('--demo', action='store_true',
                       help='Run security feature demo')
    parser.add_argument('--enable-tls', action='store_true',
                       help='Enable TLS encryption')
    parser.add_argument('--enable-containers', action='store_true',
                       help='Enable container-based execution')
    
    args = parser.parse_args()
    
    print("🪟 WinLink Desktop Application")
    print("=" * 50)
    
    # Run tests
    if args.test:
        print("🧪 Running security tests...")
        exec(open("test_windows_security.py").read())
        return 0
    
    # Run demo
    if args.demo:
        print("🎭 Running security demo...")
        exec(open("demo_security.py").read())
        return 0
    
    # Setup security
    try:
        check_and_setup_security()
    except Exception as e:
        print(f"⚠️  Security setup warning: {e}")
    
    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("WinLink")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("WinLink FYP")
    app.setStyleSheet(STYLE_SHEET)
    
    # Load configuration
    try:
        from core.config import load_config
        config = load_config()
        
        # Apply command line overrides
        if args.enable_tls:
            config.security['enable_tls'] = True
        if args.enable_containers:
            config.security['enable_containers'] = True
        
        print("\n🔧 Security Configuration:")
        for feature, enabled in config.get_security_features().items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
    
    except Exception as e:
        print(f"⚠️  Configuration loading failed: {e}")
    
    # System tray
    tray = None
    if not args.no_tray:
        tray = create_system_tray(app)
    
    # Launch appropriate interface
    if args.role == 'master':
        print("\n🎯 Starting Master Node...")
        window = MasterUI()
        window.show()
    elif args.role == 'worker':
        print("\n⚡ Starting Worker Node...")
        window = WorkerUI()
        window.show()
    else:
        if args.skip_splash:
            window = WelcomeScreen()
            window.show()
        else:
            splash = ModernSplashScreen(enable_security_checks=True)
            splash.start_loading()
    
    # Welcome notification
    if ModernNotification:
        QTimer.singleShot(3000, lambda: ModernNotification(
            "WinLink Ready!",
            "Secure distributed computing platform loaded.",
            "🔐", duration=4000
        ))
    
    print("\n🚀 Application started successfully!")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
