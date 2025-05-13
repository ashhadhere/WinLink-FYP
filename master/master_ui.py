from PyQt5 import QtWidgets, QtGui, QtCore
import sys, socket, threading

STYLE_SHEET = """
QWidget#mainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1f1f2f, stop:1 #101018);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
QFrame[glass="true"] {
    background-color: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 16px;
}
QLabel#headerLabel {
    font-size: 24px;
    font-weight: bold;
    letter-spacing: 1px;
    color: #00ffe0;
}
QLabel#infoLabel {
    font-size: 13px;
    color: #cccccc;
}
QPushButton {
    font-size: 14px;
    padding: 8px 20px;
    border-radius: 8px;
}
QPushButton#startBtn {
    background-color: #00c853;
    color: white;
}
QPushButton#stopBtn {
    background-color: #c62828;
    color: white;
}
QLineEdit {
    padding: 6px;
    border-radius: 6px;
    background-color: #f2f0f0;
    color: black;
}
"""

class MasterUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Master PC")
        self.setMinimumSize(640, 460)

        self.running = False
        self.client_socket = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header
        title = QtWidgets.QLabel("WinLink – Master PC")
        title.setObjectName("headerLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Connection Input
        self.info_card = QtWidgets.QFrame()
        self.info_card.setProperty("glass", True)
        info_layout = QtWidgets.QVBoxLayout(self.info_card)
        info_layout.setSpacing(10)

        self.ip_input = QtWidgets.QLineEdit()
        self.ip_input.setPlaceholderText("Enter Worker IP (e.g. 192.168.1.10)")
        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Enter Port (e.g. 5001)")
        self.port_input.setValidator(QtGui.QIntValidator(1, 65535))

        info_layout.addWidget(self.ip_input)
        info_layout.addWidget(self.port_input)
        self.info_card.setLayout(info_layout)
        layout.addWidget(self.info_card)

        # Status
        self.status_card = QtWidgets.QFrame()
        self.status_card.setProperty("glass", True)
        status_layout = QtWidgets.QVBoxLayout(self.status_card)
        status_layout.setSpacing(8)

        self.status_label = QtWidgets.QLabel("Status: 🔴 Idle")
        self.status_label.setObjectName("infoLabel")
        self.data_label = QtWidgets.QLabel("Waiting for data...")
        self.data_label.setObjectName("infoLabel")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.data_label)
        layout.addWidget(self.status_card)

        # Buttons
        button_row = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.connect_btn.setObjectName("startBtn")
        self.connect_btn.clicked.connect(self.connect_to_worker)

        self.disconnect_btn = QtWidgets.QPushButton("Disconnect")
        self.disconnect_btn.setObjectName("stopBtn")
        self.disconnect_btn.clicked.connect(self.disconnect_from_worker)
        self.disconnect_btn.setEnabled(False)

        button_row.addWidget(self.connect_btn)
        button_row.addWidget(self.disconnect_btn)
        layout.addLayout(button_row)

    def connect_to_worker(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        if not ip or not port:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Enter both IP and Port")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, int(port)))
            self.status_label.setText(f"Status: 🟢 Connected to {ip}:{port}")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.running = True

            threading.Thread(target=self.receive_data, daemon=True).start()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Connection Error", str(e))
            self.status_label.setText("Status: 🔴 Failed to connect")

    def receive_data(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024).decode()
                self.data_label.setText(data)
        except:
            self.status_label.setText("Status: 🔴 Connection Lost")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)

    def disconnect_from_worker(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except:
                pass
        self.status_label.setText("Status: 🔴 Disconnected")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.data_label.setText("Waiting for data...")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    win = MasterUI()
    win.show()
    sys.exit(app.exec_())
