from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from role_select import RoleSelectScreen  # your existing import
from assets.styles import STYLE_SHEET

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("welcomeScreen")
        self.setWindowTitle("WinLink - Distributed Computing Platform")
        self.setFixedSize(1000, 750)
        self.setStyleSheet(STYLE_SHEET)

        self._build_ui()
        self._center()
        self.show()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 80, 80, 80)
        layout.setSpacing(40)

        # Title
        self.title = QLabel("Welcome to")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Brand
        self.brand = QLabel("WinLink")
        self.brand.setObjectName("brand")
        self.brand.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.brand)

        # Subtitle
        self.subtitle = QLabel("Distributed Computing Platform")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        # Features
        self.features = QLabel(
            "✨ Connect Multiple PCs  •  🚀 Distribute Heavy Tasks  •  ⚡ Real-time Monitoring"
        )
        self.features.setObjectName("features")
        self.features.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.features)

        # Get Started button
        self.btn = QPushButton("Get Started")
        self.btn.setObjectName("getStartedBtn")
        self.btn.setFixedSize(280, 70)
        self.btn.clicked.connect(self.open_role_screen)

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=8, color=QColor(0, 0, 0, 150))
        self.btn.setGraphicsEffect(shadow)

        # Add button centered in main layout
        layout.addWidget(self.btn, alignment=Qt.AlignCenter)

    def _center(self):
        # Center the window on screen
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_role_screen(self):
        self.role_screen = RoleSelectScreen()
        self.role_screen.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = WelcomeScreen()
    sys.exit(app.exec_())
