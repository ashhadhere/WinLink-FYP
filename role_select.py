import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from master.master_ui import MasterUI
from worker.worker_ui import WorkerUI

class RoleSelectScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Role - WinLink")
        self.setFixedSize(720, 520)
        self.setStyleSheet("background-color: #121212; color: white;")

        layout = QVBoxLayout()

        heading = QLabel("Use this PC as:")
        heading.setFont(QFont("Helvetica", 18))
        heading.setAlignment(Qt.AlignCenter)

        master_button = QPushButton("Master PC")
        master_button.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        master_button.clicked.connect(self.launch_master)
        master_button.setFocusPolicy(Qt.NoFocus)

        worker_button = QPushButton("Worker PC")
        worker_button.setStyleSheet("""
            QPushButton {
                background-color: #43a047;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        worker_button.clicked.connect(self.launch_worker)
        worker_button.setFocusPolicy(Qt.NoFocus)

        btn_row = QHBoxLayout()
        btn_row.addWidget(master_button)
        btn_row.addWidget(worker_button)

        layout.addStretch()
        layout.addWidget(heading)
        layout.addSpacing(20)
        layout.addLayout(btn_row)
        layout.addStretch()

        self.setLayout(layout)

    def launch_master(self):
        self.master_ui = MasterUI()
        self.master_ui.show()
        self.hide()

    def launch_worker(self):
        self.worker_ui = WorkerUI()
        self.worker_ui.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RoleSelectScreen()
    win.show()
    sys.exit(app.exec_())
