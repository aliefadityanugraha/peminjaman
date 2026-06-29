# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, Signal
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class LayarLogin(QWidget):
    permintaan_login = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def _shadow(self, blur=20, offset=4, color=QColor(0, 0, 0, 60)):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset)
        shadow.setColor(color)
        return shadow

    def setup_ui(self):
        self.setWindowTitle("Pf Spaces - Masuk")
        self.resize(420, 520)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(380)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 44, 36, 44)
        card_layout.setSpacing(18)
        card.setGraphicsEffect(self._shadow(blur=40, offset=6, color=QColor(0, 0, 0, 80)))

        title_label = QLabel("Pf Spaces")
        title_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Masuk ke akun Anda")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6b7280; border: none; margin-bottom: 8px;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(44)
        card_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.returnPressed.connect(self.handle_login_click)
        card_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setVisible(False)
        self.error_label.setObjectName("errorLabel")
        card_layout.addWidget(self.error_label)

        self.tombol_login = QPushButton("Masuk")
        self.tombol_login.setObjectName("btnPrimary")
        self.tombol_login.setMinimumHeight(46)
        self.tombol_login.setCursor(Qt.PointingHandCursor)
        self.tombol_login.clicked.connect(self.handle_login_click)
        card_layout.addWidget(self.tombol_login)

        footer = QLabel("v1.0 — Pf Spaces")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #9ca3af; border: none; margin-top: 4px;")
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
            }
            QFrame#loginCard {
                background: #ffffff;
                border: none;
                border-radius: 16px;
            }
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                background: #f9fafb;
                color: #1f2937;
                selection-background-color: #6366f1;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background: #ffffff;
            }
            QLineEdit:hover {
                border-color: #a5b4fc;
                background: #ffffff;
            }
            QPushButton#btnPrimary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton#btnPrimary:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #7c3aed);
            }
            QPushButton#btnPrimary:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4338ca, stop:1 #6d28d9);
            }
            QLabel#errorLabel {
                color: #ef4444;
                font-size: 13px;
                border: none;
                padding: 8px 12px;
                background: #fef2f2;
                border-radius: 8px;
            }
        """)

    def handle_login_click(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.show_error("Harap masukkan username dan password.")
            return
        self.permintaan_login.emit(username, password)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(bool(message))
