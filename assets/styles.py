STYLE_SHEET = """
QWidget#mainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0d1117, stop:1 #161b22);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
QFrame[glass="true"] {
    background-color: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 20px;
}
QLabel#headerLabel {
    font-size: 28px;
    font-weight: bold;
    color: #58a6ff;
}
QLabel#subHeaderLabel {
    font-size: 20px;
    font-weight: 600;
    color: #c9d1d9;
}
QLabel#dataLabel {
    font-size: 16px;
    color: #8b949e;
}
QPushButton {
    font-size: 14px;
    padding: 10px 24px;
    border-radius: 10px;
    border: none;
    font-weight: 500;
}
QPushButton#startBtn {
    background-color: #238636;
    color: white;
}
QPushButton#stopBtn {
    background-color: #da3633;
    color: white;
}
QLineEdit {
    padding: 10px;
    border-radius: 10px;
    background-color: #0d1117;
    color: white;
    border: 1px solid #30363d;
    font-size: 14px;
}
"""

