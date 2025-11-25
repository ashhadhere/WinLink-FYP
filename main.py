from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont
from role_select import RoleSelectScreen  # your existing import
from assets.styles import STYLE_SHEET

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("welcomeScreen")
        self.setWindowTitle("WinLink - Distributed Computing Platform")
        
        # Remove default window frame and set up custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Start maximized (not full screen)
        self.showMaximized()
        
        self.setStyleSheet(STYLE_SHEET)
        
        # Window stays maximized - no dragging variables needed
        
        self._build_ui()
        self._setup_animations()
        
        # Start animations after showing
        QTimer.singleShot(100, self._start_animations)
        
        # Start animations after showing
        QTimer.singleShot(100, self._start_animations)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom Title Bar
        self._create_title_bar()
        
        # Content area with original margins
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(60, 40, 60, 60)
        content_layout.setSpacing(0)
        
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(content_widget, 1)

        # Header Section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 40, 0, 40)
        header_layout.setSpacing(20)

        # Welcome text
        self.welcome_label = QLabel("Welcome to")
        self.welcome_label.setObjectName("welcomeText")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 36, QFont.Light)
        self.welcome_label.setFont(font)
        header_layout.addWidget(self.welcome_label)

        # Brand name with glow effect
        self.brand = QLabel("WinLink")
        self.brand.setObjectName("brandName")
        self.brand.setAlignment(Qt.AlignCenter)
        brand_font = QFont("Segoe UI", 72, QFont.Black)
        self.brand.setFont(brand_font)
        header_layout.addWidget(self.brand)

        # Subtitle
        self.subtitle = QLabel("Enterprise-Grade Distributed Computing Platform")
        self.subtitle.setObjectName("platformSubtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 20, QFont.Medium)
        self.subtitle.setFont(subtitle_font)
        header_layout.addWidget(self.subtitle)

        content_layout.addWidget(header_frame)
        content_layout.addStretch(1)

        # Features Section
        features_frame = QFrame()
        features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(40, 30, 40, 30)
        features_layout.setSpacing(25)

        # Features title
        features_title = QLabel("Key Features")
        features_title.setObjectName("featuresTitle")
        features_title.setAlignment(Qt.AlignCenter)
        features_title_font = QFont("Segoe UI", 24, QFont.DemiBold)
        features_title.setFont(features_title_font)
        features_layout.addWidget(features_title)

        # Feature cards in horizontal layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        feature_data = [
            ("🌐", "Distributed Computing", "Connect multiple PCs across your network"),
            ("🚀", "High Performance", "Execute heavy computational tasks efficiently"),
            ("🔒", "Enterprise Security", "TLS encryption and containerized execution"),
            ("⚡", "Real-time Monitoring", "Live system resources and task progress")
        ]

        self.feature_cards = []
        for icon, title, desc in feature_data:
            card = self._create_feature_card(icon, title, desc)
            self.feature_cards.append(card)
            cards_layout.addWidget(card)

        features_layout.addLayout(cards_layout)
        content_layout.addWidget(features_frame)
        content_layout.addStretch(1)

        # Action Section
        action_frame = QFrame()
        action_frame.setObjectName("actionFrame")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(0, 30, 0, 40)
        action_layout.setSpacing(20)

        # Get Started button
        self.get_started_btn = QPushButton("Get Started")
        self.get_started_btn.setObjectName("getStartedBtn")
        self.get_started_btn.setFixedSize(320, 80)
        self.get_started_btn.clicked.connect(self.open_role_screen)
        
        # Button font
        btn_font = QFont("Segoe UI", 18, QFont.Bold)
        self.get_started_btn.setFont(btn_font)

        # Enhanced shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 245, 160, 100))
        self.get_started_btn.setGraphicsEffect(shadow)

        action_layout.addWidget(self.get_started_btn, alignment=Qt.AlignCenter)

        # Status text
        self.status_label = QLabel("Ready to revolutionize your computing workflow")
        self.status_label.setObjectName("statusText")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Segoe UI", 14, QFont.Normal)
        self.status_label.setFont(status_font)
        action_layout.addWidget(self.status_label)

        content_layout.addWidget(action_frame)

    def _create_title_bar(self):
        """Create modern custom title bar with controls"""
        self.title_bar = QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 0, 10, 0)
        title_layout.setSpacing(10)
        
        # App icon and title
        app_info_layout = QHBoxLayout()
        app_info_layout.setSpacing(12)
        
        # App icon
        app_icon = QLabel("🔗")
        app_icon.setObjectName("appIcon")
        from PyQt5.QtGui import QFont
        app_icon.setFont(QFont("Segoe UI Emoji", 16))
        app_info_layout.addWidget(app_icon)
        
        # Title
        title_label = QLabel("WinLink - Distributed Computing Platform")
        title_label.setObjectName("titleLabel")
        title_font = QFont("Segoe UI", 11, QFont.DemiBold)
        title_label.setFont(title_font)
        app_info_layout.addWidget(title_label)
        
        title_layout.addLayout(app_info_layout)
        title_layout.addStretch()
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)
        
        # Minimize button with proper height
        self.minimize_btn = QPushButton("-")
        self.minimize_btn.setFixedSize(45, 35)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: #555555;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 5px;
                margin-right: 5px;
            }
            QPushButton:hover { 
                background: #666666;
                border: 1px solid #888888;
            }
        """)
        controls_layout.addWidget(self.minimize_btn)
        
        # Close button with proper height
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(45, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #c0392b;
                border-radius: 4px;
            }
            QPushButton:hover { 
                background: #c0392b;
                border: 1px solid #a93226;
            }
        """)
        controls_layout.addWidget(self.close_btn)
        
        title_layout.addLayout(controls_layout)
        
        # Title bar is not draggable - window stays maximized

    # Window stays maximized - no dragging or resizing allowed

    def _create_feature_card(self, icon, title, description):
        card = QFrame()
        card.setObjectName("featureCard")
        card.setFixedSize(250, 160)
        
        # Card layout
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("featureIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Segoe UI Emoji", 32)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("featureTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("featureDesc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_font = QFont("Segoe UI", 11, QFont.Normal)
        desc_label.setFont(desc_font)
        layout.addWidget(desc_label)

        # Card shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        return card

    def _setup_animations(self):
        # Set initial opacity for animated elements
        self.welcome_effect = QGraphicsOpacityEffect()
        self.brand_effect = QGraphicsOpacityEffect()
        self.subtitle_effect = QGraphicsOpacityEffect()
        
        self.welcome_label.setGraphicsEffect(self.welcome_effect)
        self.brand.setGraphicsEffect(self.brand_effect)
        self.subtitle.setGraphicsEffect(self.subtitle_effect)
        
        # Set initial opacity to 0
        self.welcome_effect.setOpacity(0)
        self.brand_effect.setOpacity(0)
        self.subtitle_effect.setOpacity(0)
        
        # Hide feature cards initially
        self.card_effects = []
        for card in self.feature_cards:
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0)
            card.setGraphicsEffect(effect)
            self.card_effects.append(effect)

    def _start_animations(self):
        # Animate welcome text
        self._animate_fade_in(self.welcome_effect, 800, 0)
        
        # Animate brand name
        QTimer.singleShot(200, lambda: self._animate_fade_in(self.brand_effect, 1000, 0))
        
        # Animate subtitle
        QTimer.singleShot(400, lambda: self._animate_fade_in(self.subtitle_effect, 800, 0))
        
        # Animate feature cards with stagger
        for i, effect in enumerate(self.card_effects):
            QTimer.singleShot(600 + i * 150, lambda e=effect: self._animate_fade_in(e, 600, 0))

    def _animate_fade_in(self, effect, duration, delay):
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        if delay > 0:
            QTimer.singleShot(delay, animation.start)
        else:
            animation.start()
            
        # Store animation reference to prevent garbage collection
        if not hasattr(self, '_animations'):
            self._animations = []
        self._animations.append(animation)



    def open_role_screen(self):
        self.role_screen = RoleSelectScreen()
        self.role_screen.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = WelcomeScreen()
    sys.exit(app.exec_())
