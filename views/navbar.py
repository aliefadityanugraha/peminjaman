from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

NAVBAR_STYLE = """
    QFrame#navbar {
        background: #ffffff;
        border-bottom: 1px solid #e5e7eb;
    }
    QLabel#navTitle {
        color: #1f2937;
        font-weight: bold;
        border: none;
        background: transparent;
    }
    QLabel#navRole {
        color: #6b7280;
        font-size: 12px;
        border: none;
        background: transparent;
    }
    QPushButton#navBtn {
        background: transparent;
        color: #6b7280;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton#navBtn:hover {
        background: #f3f4f6;
        color: #1f2937;
    }
    QPushButton#navBtn:checked {
        background: #eef2ff;
        color: #6366f1;
        font-weight: 600;
    }
    QPushButton#logoutBtn {
        background: #fef2f2;
        color: #ef4444;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton#logoutBtn:hover {
        background: #fee2e2;
        border-color: #fca5a5;
    }
"""


class Navbar(QFrame):
    page_changed = Signal(int)
    logout_clicked = Signal()

    def __init__(self, title, role_text, username, nav_items):
        super().__init__()
        self.setObjectName("navbar")
        self.setFixedHeight(60)

        self.nav_items = nav_items
        self.buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        brand = QVBoxLayout()
        brand.setSpacing(0)
        title_label = QLabel(title)
        title_label.setObjectName("navTitle")
        title_label.setFont(QFont("Segoe UI", 15))
        brand.addWidget(title_label)
        role_label = QLabel(role_text)
        role_label.setObjectName("navRole")
        brand.addWidget(role_label)
        layout.addLayout(brand)

        layout.addSpacing(32)

        for name, text, idx in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._on_page_click(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        if username:
            user_label = QLabel(f"👤 {username}")
            user_label.setStyleSheet("color: #9ca3af; font-size: 12px; border: none; padding: 0 8px;")
            layout.addWidget(user_label)

        self.logout_btn = QPushButton("Keluar")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(self.logout_btn)

    def _on_page_click(self, index):
        self.page_changed.emit(index)

    def set_active(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
