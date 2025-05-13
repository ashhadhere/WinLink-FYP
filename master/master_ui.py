from PyQt5 import QtWidgets, QtGui, QtCore
import sys, socket, threading



class MasterUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Master PC")
        self.setMinimumSize(720, 520)

        self.running = False
        self.client_socket = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        title = QtWidgets.QLabel("WinLink")
        title.setObjectName("headerLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        sub_heading = QtWidgets.QLabel("Connected PC")
        sub_heading.setObjectName("subHeaderLabel")
        sub_heading.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(sub_heading)

        # Input Card
        self.input_card = QtWidgets.QFrame()
        self.input_card.setProperty("glass", True)
        input_layout = QtWidgets.QVBoxLayout(self.input_card)
        input_layout.setSpacing(14)

        self.ip_input = QtWidgets.QLineEdit()
        self.ip_input.setPlaceholderText("Enter Worker IP (e.g. 192.168.1.10)")
        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Enter Port (e.g. 5001)")
        self.port_input.setValidator(QtGui.QIntValidator(1, 65535))

        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(self.port_input)
        layout.addWidget(self.input_card)

        # Status Card
        self.status_card = QtWidgets.QFrame()
        self.status_card.setProperty("glass", True)
        status_layout = QtWidgets.QVBoxLayout(self.status_card)
        status_layout.setSpacing(10)

        self.status_label = QtWidgets.QLabel("Status: 🔴 Idle")
        self.status_label.setObjectName("dataLabel")
        self.data_label = QtWidgets.QLabel("Waiting for data...")
        self.data_label.setObjectName("dataLabel")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.data_label)
        layout.addWidget(self.status_card)

        # Action Buttons
        button_row = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.connect_btn.setObjectName("startBtn")
        self.connect_btn.clicked.connect(self.connect_to_worker)

        self.disconnect_btn = QtWidgets.QPushButton("Disconnect")
        self.disconnect_btn.setObjectName("stopBtn")
        self.disconnect_btn.clicked.connect(self.disconnect_from_worker)
        self.disconnect_btn.setEnabled(False)

        button_row.addStretch(1)
        button_row.addWidget(self.connect_btn)
        button_row.addWidget(self.disconnect_btn)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.apply_shadow(self.input_card)
        self.apply_shadow(self.status_card)

    def apply_shadow(self, widget):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        widget.setGraphicsEffect(shadow)

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
