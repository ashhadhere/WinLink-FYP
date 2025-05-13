from PyQt5 import QtWidgets, QtGui, QtCore
import sys, socket, threading, psutil, time

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
    transition: all 0.3s ease-in-out;
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

class WorkerUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("WinLink – Worker PC")
        self.setMinimumSize(640, 520)

        self.server = None
        self.running = False
        self.conn = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        title = QtWidgets.QLabel("WinLink – Worker PC")
        title.setObjectName("headerLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Info Card
        self.info_card = QtWidgets.QFrame()
        self.info_card.setProperty("glass", True)
        info_layout = QtWidgets.QVBoxLayout(self.info_card)
        info_layout.setSpacing(10)

        self.ip_label = QtWidgets.QLabel("IP Address: 0.0.0.0")
        self.ip_label.setObjectName("infoLabel")

        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Enter Port (e.g. 5001)")
        self.port_input.setValidator(QtGui.QIntValidator(1, 65535))

        info_layout.addWidget(self.ip_label)
        info_layout.addWidget(self.port_input)
        self.info_card.setLayout(info_layout)
        layout.addWidget(self.info_card)

        # Resource Toggles
        toggle_card = QtWidgets.QFrame()
        toggle_card.setProperty("glass", True)
        toggle_layout = QtWidgets.QFormLayout(toggle_card)
        toggle_layout.setSpacing(10)

        self.cpu_toggle = QtWidgets.QCheckBox("CPU")
        self.cpu_toggle.setChecked(True)
        self.gpu_toggle = QtWidgets.QCheckBox("GPU")
        self.ram_toggle = QtWidgets.QCheckBox("RAM")
        self.storage_toggle = QtWidgets.QCheckBox("Storage")

        for toggle in [self.cpu_toggle, self.gpu_toggle, self.ram_toggle, self.storage_toggle]:
            toggle.setStyleSheet("font-size: 13px; color: white;")

        toggle_layout.addRow(self.cpu_toggle)
        toggle_layout.addRow(self.gpu_toggle)
        toggle_layout.addRow(self.ram_toggle)
        toggle_layout.addRow(self.storage_toggle)
        layout.addWidget(toggle_card)

        # Status Card
        self.status_card = QtWidgets.QFrame()
        self.status_card.setProperty("glass", True)
        status_layout = QtWidgets.QVBoxLayout(self.status_card)
        status_layout.setSpacing(8)

        self.status_label = QtWidgets.QLabel("Status: 🔴 Idle")
        self.status_label.setObjectName("infoLabel")

        string_layout = QtWidgets.QHBoxLayout()
        self.full_conn_string = QtWidgets.QLineEdit("Connection String: N/A")
        self.full_conn_string.setReadOnly(True)
        self.full_conn_string.setStyleSheet("color: white; background-color: transparent; border: none;")
        copy_btn = QtWidgets.QPushButton("📋")
        copy_btn.setFixedWidth(30)
        copy_btn.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.full_conn_string.text()))

        string_layout.addWidget(self.full_conn_string)
        string_layout.addWidget(copy_btn)

        status_layout.addWidget(self.status_label)
        status_layout.addLayout(string_layout)
        layout.addWidget(self.status_card)

        # Buttons
        button_row = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start Sharing")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_server)

        self.stop_btn = QtWidgets.QPushButton("Stop Sharing")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)

        button_row.addWidget(self.start_btn)
        button_row.addWidget(self.stop_btn)
        layout.addLayout(button_row)

        self.setLayout(layout)
        self.update_ip()

    def update_ip(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            self.ip_label.setText(f"IP Address: {ip}")
        except:
            self.ip_label.setText("IP Address: Unavailable")

    def start_server(self):
        port_text = self.port_input.text().strip()
        if not port_text:
            QtWidgets.QMessageBox.warning(self, "Missing Port", "Please enter a valid port.")
            return

        ip = socket.gethostbyname(socket.gethostname())
        port = int(port_text)

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((ip, port))
            self.server.listen(1)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Port Error", f"Port {port} is already in use.")
            self.reset_ui()
            return

        self.status_label.setText("Status: 🟡 Waiting for Master...")
        self.full_conn_string.setText(f"{ip}:{port}")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.running = True

        def handle():
            try:
                self.conn, addr = self.server.accept()
                self.status_label.setText(f"Status: 🟢 Connected to {addr[0]}:{addr[1]}")
                while self.running:
                    cpu = psutil.cpu_percent() if self.cpu_toggle.isChecked() else "-"
                    ram = psutil.virtual_memory().percent if self.ram_toggle.isChecked() else "-"
                    try:
                        battery = psutil.sensors_battery()
                        batt = battery.percent if battery else "N/A"
                    except:
                        batt = "N/A"
                    data = f"CPU: {cpu}%, RAM: {ram}%, Battery: {batt}%"
                    self.conn.send(data.encode())
                    time.sleep(2)
            except:
                if self.running:
                    self.status_label.setText("Status: 🔴 Disconnected")
                    self.full_conn_string.setText("Connection String: N/A")
                    self.reset_ui()

        threading.Thread(target=handle, daemon=True).start()

    def stop_server(self):
        self.running = False
        if self.conn:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        self.status_label.setText("Status: 🔴 Idle")
        self.full_conn_string.setText("Connection String: N/A")
        self.reset_ui()

    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    win = WorkerUI()
    win.show()
    sys.exit(app.exec_())