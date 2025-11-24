import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from master.master_ui import MasterUI
from worker.worker_ui import WorkerUI
from assets.styles import STYLE_SHEET


class RoleCard(QFrame):
    def __init__(self, role, title, description, icon, features=None, parent=None):
        super().__init__(parent)
        self.setObjectName("roleCard")
        self.setProperty("role", role)  # 'master' or 'worker'
        self.setFixedSize(360, 280)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui(title, description, icon, features)
        self.setup_shadow()

    def setup_ui(self, title, desc, icon, features):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Icon
        icon_lbl = QLabel(icon, self)
        icon_lbl.setObjectName("cardIcon")
        icon_lbl.setAlignment(Qt.AlignCenter)

        # Title
        title_lbl = QLabel(title, self)
        title_lbl.setObjectName("cardTitle")
        title_lbl.setAlignment(Qt.AlignCenter)

        # Description
        desc_lbl = QLabel(desc, self)
        desc_lbl.setObjectName("cardDesc")
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignCenter)

        # Features
        if features:
            feats = "\n".join(f"• {f}" for f in features)
            features_lbl = QLabel(feats, self)
            features_lbl.setObjectName("cardFeatures")
            features_lbl.setWordWrap(True)
            features_lbl.setAlignment(Qt.AlignLeft)

        # Add
        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        if features:
            layout.addWidget(features_lbl)
        layout.addStretch()

    def setup_shadow(self):
        sh = QGraphicsDropShadowEffect(blurRadius=35, xOffset=0, yOffset=12, color=QColor(0,0,0,150))
        self.setGraphicsEffect(sh)

    def enterEvent(self, event):
        # enlarge shadow
        sh = self.graphicsEffect()
        sh.setBlurRadius(45); sh.setOffset(0,16)
        super().enterEvent(event)

    def leaveEvent(self, event):
        sh = self.graphicsEffect()
        sh.setBlurRadius(35); sh.setOffset(0,12)
        super().leaveEvent(event)


class RoleSelectScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("roleSelectScreen")
        self.setWindowTitle("WinLink – Select Your Role")
        self.setFixedSize(1100, 800)
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()
        self.setup_animations()
        QTimer.singleShot(150, self.start_entrance_animations)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 80, 60, 80)
        main_layout.setSpacing(50)

        # Header
        self.main_title = QLabel("Choose Your Role", self)
        self.main_title.setObjectName("mainTitle")
        self.main_title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel(
            "Select how you want to participate in the distributed computing network", 
            self
        )
        self.subtitle.setObjectName("subTitle")
        self.subtitle.setWordWrap(True)
        self.subtitle.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.main_title)
        main_layout.addWidget(self.subtitle)

        # Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(60)
        cards_layout.setContentsMargins(40, 40, 40, 40)

        master = RoleCard(
            role="master",
            title="Master PC",
            description="Control and distribute computing tasks across the network",
            icon="🎯",
            features=[
                "Create and manage tasks",
                "Monitor worker performance",
                "Real-time distribution",
                "Advanced analytics"
            ]
        )
        master.mousePressEvent = lambda e: self.open_master_ui()

        worker = RoleCard(
            role="worker",
            title="Worker PC",
            description="Contribute your PC’s processing power",
            icon="⚡",
            features=[
                "Share CPU & RAM",
                "Safe task execution",
                "Monitor usage",
                "Auto load-balancing"
            ]
        )
        worker.mousePressEvent = lambda e: self.open_worker_ui()

        cards_layout.addStretch()
        cards_layout.addWidget(master)
        cards_layout.addWidget(worker)
        cards_layout.addStretch()

        main_layout.addLayout(cards_layout)

        # Back Button
        self.back_btn = QPushButton("← Back to Welcome", self)
        self.back_btn.setObjectName("backBtn")
        self.back_btn.setFixedSize(200, 50)
        self.back_btn.clicked.connect(self.go_back)

        # Shadow
        back_shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,80))
        self.back_btn.setGraphicsEffect(back_shadow)

        main_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)

    def setup_animations(self):
        # fade in title
        self.title_anim = QPropertyAnimation(self.main_title, b"windowOpacity")
        self.title_anim.setDuration(800)
        self.title_anim.setStartValue(0.0)
        self.title_anim.setEndValue(1.0)
        self.title_anim.setEasingCurve(QEasingCurve.OutCubic)

        # slide in subtitle
        self.sub_anim = QPropertyAnimation(self.subtitle, b"pos")
        self.sub_anim.setDuration(600)
        self.sub_anim.setEasingCurve(QEasingCurve.OutCubic)

        # fade in back button
        self.btn_anim = QPropertyAnimation(self.back_btn, b"windowOpacity")
        self.btn_anim.setDuration(600)
        self.btn_anim.setStartValue(0.0)
        self.btn_anim.setEndValue(1.0)
        self.btn_anim.setEasingCurve(QEasingCurve.OutCubic)

    def start_entrance_animations(self):
        self.main_title.setWindowOpacity(0.0)
        self.back_btn.setWindowOpacity(0.0)

        self.title_anim.start()
        QTimer.singleShot(200, self._start_sub_anim)
        QTimer.singleShot(400, self._start_btn_anim)

    def _start_sub_anim(self):
        cp = self.subtitle.pos()
        self.subtitle.move(cp.x(), cp.y() - 30)
        self.sub_anim.setStartValue(self.subtitle.pos())
        self.sub_anim.setEndValue(cp)
        self.sub_anim.start()

    def _start_btn_anim(self):
        self.btn_anim.start()

    def open_master_ui(self):
        self.master_ui = MasterUI()
        self.master_ui.show()
        self.close()

    def open_worker_ui(self):
        self.worker_ui = WorkerUI()
        self.worker_ui.show()
        self.close()

    def go_back(self):
        from main import WelcomeScreen
        self.welcome = WelcomeScreen()
        self.welcome.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RoleSelectScreen()
    win.show()
    sys.exit(app.exec_())
