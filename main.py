import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from role_select import RoleSelectScreen

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinLink")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #121212; color: white;")
        layout = QVBoxLayout()

        title = QLabel("Welcome to")
        title.setFont(QFont("Helvetica", 18))
        title.setAlignment(Qt.AlignCenter)

        brand = QLabel("WinLink")
        brand.setFont(QFont("Helvetica", 32, QFont.Bold))
        brand.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Get Started")
        btn.setFixedHeight(40)
        btn.setStyleSheet("background-color: #1f5c5c; color: white; font-size: 16px; border-radius: 8px;")
        btn.clicked.connect(self.open_role_screen)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(brand)
        layout.addStretch()
        layout.addWidget(btn)
        layout.addStretch()
        self.setLayout(layout)

    def open_role_screen(self):
        self.role_screen = RoleSelectScreen()
        self.role_screen.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WelcomeScreen()
    win.show()
    sys.exit(app.exec_())
