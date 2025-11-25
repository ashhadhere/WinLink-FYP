# assets/styles.py

STYLE_SHEET = """
/* ======================
   Global
   ====================== */
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 9pt;  /* Comfortable base font size */
    color: #e6e6fa;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #141e30, stop:1 #243b55);
}

/* ======================
   Main Window
   ====================== */
QWidget#mainWindow {
    padding: 20px;
}

/* ======================
   Glass Panels (QFrame[glass="true"])
   ====================== */
QFrame[glass="true"] {
    background-color: rgba(255,255,255,0.08);
    border: none;
    border-radius: 16px;
    padding: 24px;
}

/* ======================
   Group Boxes
   ====================== */
QGroupBox {
    background: rgba(255,255,255,0.05);
    border: none;
    border-radius: 12px;
    margin-top: 16px;
    padding: 16px;
    color: #c1d5e0;
    font-weight: 600;
    font-size: 10pt;  /* Group box titles */
}

/* ======================
   Labels
   ====================== */
QLabel#headerLabel {
    font-size: 28px;
    font-weight: 700;
    color: #00ffe0;
    letter-spacing: 1px;
}

QLabel#subHeaderLabel {
    font-size: 22px;
    font-weight: 600;
    color: #c1d5e0;
    margin-bottom: 12px;
}

QLabel#infoLabel {
    font-size: 13px;
    color: #b8c5d6;
}

QLabel#dataLabel {
    font-size: 16px;
    color: #a0b0c0;
}

/* ======================
   Buttons
   ====================== */
QPushButton {
    font-size: 15px;
    font-weight: 600;
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    background: rgba(255,255,255,0.1);
}
QPushButton:hover {
    background: rgba(255,255,255,0.2);
}
QPushButton:pressed {
    background: rgba(255,255,255,0.3);
}

/* Start & Stop buttons */
QPushButton#startBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00d4aa, stop:1 #00f5a0);
    color: #141e30;
}
QPushButton#startBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00ff88, stop:1 #00d4aa);
}

QPushButton#stopBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #ff6b6b, stop:1 #ff4444);
    color: white;
}
QPushButton#stopBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #ff8a80, stop:1 #ff6b6b);
}

/* ======================
   Inputs & TextAreas
   ====================== */
QLineEdit, QSpinBox {
    background: rgba(255,255,255,0.1);
    border: none;
    border-radius: 8px;
    padding: 8px;
    color: white;
}
QLineEdit:focus, QSpinBox:focus {
    background: rgba(255,255,255,0.15);
    border: 2px solid rgba(0,212,170,0.5);
}

QTextEdit {
    background: rgba(255,255,255,0.08);
    border: none;
    border-radius: 10px;
    padding: 12px;
    color: #c1d5e0;
}

/* ======================
   Progress Bars
   ====================== */
QProgressBar {
    background: rgba(255,255,255,0.1);
    border: none;
    border-radius: 10px;
    height: 20px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00f5a0, stop:1 #667eea);
    border-radius: 10px;
}

/* ======================
   System Tray Menu
   ====================== */
QMenu {
    background: rgba(26,26,58,0.95);
    border: none;
    border-radius: 8px;
    padding: 4px;
    color: white;
}
QMenu::item {
    padding: 8px 16px;
}
QMenu::item:selected {
    background: rgba(0,212,170,0.3);
}

/* ======================
   Custom Cards (#modernCard)
   ====================== */
QFrame#modernCard {
    background: rgba(255,255,255,0.1);
    border: none;
    border-radius: 16px;
    padding: 24px;
    margin: 8px;
}
QFrame#modernCard:hover {
    background: rgba(255,255,255,0.15);
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    transform: translateY(-2px);
}

/* ======================
   Tooltips
   ====================== */
QToolTip {
    background: rgba(0,212,170,0.9);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}

/* ======================
   Global & Main Window
   ====================== */
QWidget {
    font-family: 'Segoe UI', sans-serif;
    color: #e6e6fa;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #141e30, stop:1 #243b55);
}
QWidget#mainWindow {
    padding: 24px;
}

/* ======================
   Glass Panels
   ====================== */
QFrame[glass="true"] {
    background-color: rgba(255,255,255,0.08);
    border: none;
    border-radius: 16px;
    padding: 24px;
}
QFrame[glass="true"]:hover {
    background-color: rgba(255,255,255,0.10);
}

/* ======================
   Labels
   ====================== */
QLabel#headerLabel {
    font-size: 28px;
    font-weight: 700;
    color: #00ffe0;
    letter-spacing: 1px;
}
QLabel#infoLabel {
    font-size: 13px;
    color: #b8c5e3;
}

/* ======================
   Buttons
   ====================== */
QPushButton {
    font-size: 15px;
    font-weight: 600;
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    background: rgba(255,255,255,0.10);
}
QPushButton:hover {
    background: rgba(255,255,255,0.20);
}
QPushButton:pressed {
    background: rgba(255,255,255,0.30);
}

/* Start/Stop Buttons */
QPushButton#startBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00d4aa, stop:1 #00f5a0);
    color: #141e30;
}
QPushButton#startBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00ff88, stop:1 #00d4aa);
}

QPushButton#stopBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #ff6b6b, stop:1 #ff4444);
    color: white;
}
QPushButton#stopBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #ff8a80, stop:1 #ff6b6b);
}

/* ======================
   Inputs & TextAreas
   ====================== */
QLineEdit, QSpinBox {
    background: rgba(255,255,255,0.12);
    border: none;
    border-radius: 8px;
    padding: 8px;
    color: #141e30;
}
QLineEdit:focus, QSpinBox:focus {
    background: rgba(255,255,255,0.18);
    border: 2px solid rgba(0,212,170,0.5);
}

QTextEdit {
    background: rgba(255,255,255,0.08);
    border: none;
    border-radius: 10px;
    padding: 12px;
    color: #c1d5e0;
}

/* ======================
   Progress Bars
   ====================== */
QProgressBar {
    background: rgba(255,255,255,0.10);
    border: none;
    border-radius: 10px;
    height: 22px;
    text-align: center;
    color: white;
    font-weight: 600;
    font-size: 12px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                               stop:0 #00f5a0, stop:1 #667eea);
    border-radius: 10px;
}

/* ======================
   Group Boxes
   ====================== */
QGroupBox {
    background: rgba(255,255,255,0.05);
    border: none;
    border-radius: 12px;
    margin-top: 16px;
    padding: 16px;
    color: #c1d5e0;
    font-weight: 600;
    font-size: 10pt;  /* Group box titles */
}

/* ======================
   Scroll Bars & Misc
   ====================== */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(0,212,170,0.6);
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0,212,170,0.8);
}

/* ======================
   Tooltips
   ====================== */
QToolTip {
    background: rgba(0,212,170,0.9);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}
/* Copy button in connection panel */
QPushButton#copyBtn {
    background: rgba(255,255,255,0.15);
    color: white;
    font-size: 13px;
    min-width: 60px;
    min-height: 30px;
    border-radius: 6px;
}
QPushButton#copyBtn:hover {
    background: rgba(255,255,255,0.25);
}
QPushButton#copyBtn:pressed {
    background: rgba(255,255,255,0.35);
}

/* Tasks panel styling */
QTextEdit#tasksDisplay {
    background: rgba(20, 20, 32, 0.8);
    color: #e6e6fa;
    border: none;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}

/* ======================
   Enhanced Table Styling
   ====================== */
QTableWidget {
    background-color: rgba(30, 30, 40, 0.8);
    alternate-background-color: rgba(45, 45, 55, 0.8);
    color: #f0f0f0;
    gridline-color: rgba(100, 100, 120, 0.3);
    font-size: 10pt;
    selection-background-color: rgba(100, 255, 160, 0.3);
    border: 1px solid rgba(100, 100, 120, 0.3);
    border-radius: 8px;
}

QTableWidget::item {
    padding: 8px;
    border: none;
    color: #f0f0f0;
}

QTableWidget::item:selected {
    background-color: rgba(100, 255, 160, 0.3);
    color: #ffffff;
}

QHeaderView::section {
    background-color: rgba(50, 50, 65, 0.9);
    color: #f0f0f0;
    padding: 10px 8px;
    border: 1px solid rgba(100, 100, 120, 0.3);
    font-weight: bold;
    font-size: 10pt;
    text-align: center;
}

QHeaderView::section:hover {
    background-color: rgba(60, 60, 75, 0.9);
}

/* ======================
   Connection Settings Widgets
   ====================== */
QLabel#ipLabel {
    background: rgba(20, 20, 32, 0.8);
    color: #e6e6fa;
    padding: 6px 8px;
    border-radius: 6px;
    font-weight: 500;
}

QLineEdit#portInput {
    background: rgba(20, 20, 32, 0.8);
    color: #e6e6fa;
    padding: 6px 8px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
}

/* ── Main Welcome Window ── */
QWidget#welcomeScreen {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a0a2e,
        stop:0.3 #16213e,
        stop:0.7 #0f3460,
        stop:1 #533483
    );
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* ── Welcome Screen Components ── */
QLabel#welcomeText {
    color: rgba(255, 255, 255, 0.9);
    background: transparent;
}

QLabel#brandName {
    color: #00f5a0;
    background: transparent;
}

QLabel#platformSubtitle {
    color: rgba(255, 255, 255, 0.8);
    background: transparent;
}

QFrame#featuresFrame {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
}

QLabel#featuresTitle {
    color: rgba(255, 255, 255, 0.9);
    background: transparent;
}

QFrame#featureCard {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
}

QFrame#featureCard:hover {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(0, 245, 160, 0.3);
}

QLabel#featureIcon {
    color: #00f5a0;
    background: transparent;
}

QLabel#featureTitle {
    color: white;
    background: transparent;
}

QLabel#featureDesc {
    color: rgba(255, 255, 255, 0.7);
    background: transparent;
}

QLabel#statusText {
    color: rgba(255, 255, 255, 0.6);
    background: transparent;
}

/* ── Header Text ── */
QLabel#title {
    font-size: 32px;
    font-weight: 300;
    letter-spacing: 3px;
    background: transparent;
}
QLabel#brand {
    font-size: 88px;
    font-weight: 900;
    letter-spacing: 8px;
    color: #00f5a0;
    background: transparent;
}
QLabel#subtitle {
    font-size: 24px;
    font-weight: 400;
    letter-spacing: 2px;
    background: transparent;
}

/* ── Features Line ── */
QLabel#features {
    font-size: 16px;
    font-weight: 500;
    color: rgba(0,245,160,0.9);
    background: transparent;
}

/* ── Get Started Button ── */
QPushButton#getStartedBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00f5a0,
        stop:0.5 #00d4aa,
        stop:1 #667eea
    );
    color: #000000;
    font-size: 20px;
    font-weight: 800;
    border-radius: 18px;
    padding: 20px 50px;
}
QPushButton#getStartedBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00ff88,
        stop:0.5 #00f5a0,
        stop:1 #00d4aa
    );
}
QPushButton#getStartedBtn:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4aa,
        stop:0.5 #00c4aa,
        stop:1 #557eea
    );
}

QWidget#roleSelectScreen {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(10,10,46,0.98),
        stop:0.3 rgba(22,33,62,0.98),
        stop:0.7 rgba(15,52,96,0.98),
        stop:1 rgba(83,52,131,0.98)
    );
    font-family: 'Segoe UI', sans-serif;
}

/* Make every QLabel transparent by default */
QLabel {
    background: transparent;
}

/* ── Header Labels ── */
QLabel#mainTitle {
    color: #00f5a0;
    font-size: 48px;
    font-weight: 800;
    letter-spacing: 3px;
}
QLabel#subTitle {
    color: rgba(255,255,255,0.8);
    font-size: 18px;
    font-weight: 400;
    letter-spacing: 1px;
}

/* ── Role Cards ── */
QFrame#roleCard {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.12),
        stop:0.5 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.05)
    );
    border: 2px solid rgba(0, 245, 160, 0.3);
    border-radius: 24px;
}

QFrame#roleCard[role="master"] {
    border: 2px solid rgba(0, 245, 160, 0.4);
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 245, 160, 0.15),
        stop:0.5 rgba(255, 255, 255, 0.08),
        stop:1 rgba(102, 126, 234, 0.15)
    );
}

QFrame#roleCard[role="worker"] {
    border: 2px solid rgba(76, 175, 80, 0.4);
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(76, 175, 80, 0.15),
        stop:0.5 rgba(255, 255, 255, 0.08),
        stop:1 rgba(139, 195, 74, 0.15)
    );
}

QFrame#roleCard:hover {
    border: 2px solid rgba(255, 255, 255, 0.5);
}

QFrame#roleCard[role="master"]:hover {
    border: 2px solid rgba(0, 245, 160, 0.8);
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 245, 160, 0.25),
        stop:0.5 rgba(255, 255, 255, 0.12),
        stop:1 rgba(102, 126, 234, 0.25)
    );
}

QFrame#roleCard[role="worker"]:hover {
    border: 2px solid rgba(76, 175, 80, 0.8);
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(76, 175, 80, 0.25),
        stop:0.5 rgba(255, 255, 255, 0.12),
        stop:1 rgba(139, 195, 74, 0.25)
    );
}

QFrame#iconContainer {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 40px;
}

QFrame#featuresContainer {
    background: rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}

QLabel#statusIndicator {
    color: rgba(0, 245, 160, 0.9);
    background: transparent;
}

/* Card contents */
QLabel#cardIcon {
    color: white;
    background: transparent;
}
QLabel#cardTitle {
    color: white;
    background: transparent;
    letter-spacing: 1px;
}
QLabel#cardDesc {
    color: rgba(255,255,255,0.85);
    background: transparent;
}
QLabel#cardFeatures {
    color: rgba(255,255,255,0.75);
    background: transparent;
}
QLabel#actionHint {
    color: rgba(255,255,255,0.6);
    background: transparent;
}

/* ── Enhanced Buttons ── */
QPushButton#infoBtn {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
}
QPushButton#infoBtn:hover {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(0, 245, 160, 0.4);
    color: white;
}

/* ── Back Button ── */
QPushButton#backBtn {
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.9);
    border: 2px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    padding: 12px 24px;
}
QPushButton#backBtn:hover {
    background: rgba(255,255,255,0.18);
    border: 2px solid rgba(0,245,160,0.5);
    color: white;
}

/* ── Main Window ── */
QWidget#mainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #141e30, stop:1 #243b55
    );
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* ── Headers ── */
QLabel#headerLabel {
    font-size: 24px;
    font-weight: bold;
    color: #00ffe0;
}

/* ── GroupBoxes ── */
QGroupBox {
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    margin-top: 16px;
    padding: 12px;
    color: white;
    font-weight: bold;
}

/* ── Buttons ── */
QPushButton#startBtn {
    background: #00c853;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
}
QPushButton#stopBtn {
    background: #c62828;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
}
QPushButton#disconnectBtn, QPushButton#clearBtn {
    background: rgba(255,255,255,0.1);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
}
QPushButton:hover {
    background: rgba(255,255,255,0.15);
}

/* ── LineEdits ── */
QLineEdit, QSpinBox {
    background: rgba(255,255,255,0.1);
    color: white;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 6px;
    padding: 4px;
}

/* ── ListWidget ── */
QListWidget {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    color: white;
    font-size: 9pt;
    padding: 4px;
}
QListWidget::item {
    padding: 6px;
}
QListWidget::item:selected {
    background: rgba(88,166,255,0.3);
}

/* ── TextEdit ── */
QTextEdit {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    color: #ddd;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}

/* ── Table ── */
QTableWidget {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    font-size: 9pt;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background: rgba(255,255,255,0.1);
    color: white;
    padding: 8px;
    border: none;
    font-size: 9pt;
    font-weight: 600;
}

/* ── ComboBox ── */
QComboBox {
    background: rgba(255,255,255,0.1);
    color: white;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 6px;
    padding: 6px;
    font-size: 9pt;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border: none;
}
QComboBox QAbstractItemView {
    background: rgba(20,20,32,0.95);
    color: white;
    selection-background-color: rgba(0,245,160,0.3);
    font-size: 9pt;
}

/* Scrollbar for task table */
QScrollBar#taskScrollBar {
    background: rgba(255,255,255,0.05);
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}
QScrollBar#taskScrollBar::handle {
    background: rgba(0,245,160,0.6);
    min-height: 30px;
    border-radius: 6px;
}
QScrollBar#taskScrollBar::handle:hover {
    background: rgba(0,245,160,0.8);
}
QScrollBar#taskScrollBar::add-line, QScrollBar#taskScrollBar::sub-line {
    height: 0px;
}
QScrollBar#taskScrollBar::add-page, QScrollBar#taskScrollBar::sub-page {
    background: none;
}

/* Placeholder label styling */
QLabel#placeholderLabel {
    color: rgba(255,255,255,0.5);
    font-size: 16px;
    font-style: italic;
    background: transparent;
}

/* ======================
   Modern Title Bar Styling
   ====================== */
QFrame#titleBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 rgba(30, 30, 50, 0.95),
                               stop:1 rgba(20, 20, 40, 0.95));
    border: none;
    border-bottom: 1px solid rgba(100, 255, 160, 0.2);
}

QLabel#appIcon {
    color: #00f5a0;
    padding: 5px;
}

QLabel#titleLabel {
    color: #e6e6fa;
    font-weight: bold;
    padding: 5px 0;
}

QPushButton#windowControl {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial, sans-serif;
    border-radius: 4px;
    margin: 1px;
}

QPushButton#windowControl:hover {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff;
}

QPushButton#windowControl:pressed {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

QPushButton#closeControl {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial, sans-serif;
    border-radius: 4px;
    margin: 1px;
}

QPushButton#closeControl:hover {
    background: rgba(231, 76, 60, 0.9);
    border: 1px solid rgba(192, 57, 43, 0.9);
    color: #ffffff;
}

QPushButton#closeControl:pressed {
    background: rgba(192, 57, 43, 0.9);
    border: 1px solid rgba(169, 50, 38, 0.9);
}

/* Content area styling */
QWidget#contentArea {
    background: transparent;
}

"""
