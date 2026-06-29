from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


def shadow(blur=8, offset=1, color=QColor(0, 0, 0, 20)):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(blur)
    s.setOffset(0, offset)
    s.setColor(color)
    return s


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def status_badge(text, color, bg):
    badge = QLabel(text)
    badge.setStyleSheet(f"""
        color: {color}; font-weight: 600; font-size: 12px;
        border: 1px solid {color}; border-radius: 6px; padding: 4px 12px;
        background: {bg};
    """)
    return badge


def action_button(text, bg, hover, fixed_size=None):
    btn = QPushButton(text)
    if fixed_size:
        btn.setFixedSize(*fixed_size)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: white; border: none;
            border-radius: 6px; font-size: 12px; font-weight: 600;
            padding: 6px 16px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return btn


def primary_button(text, min_w=180, min_h=46):
    btn = QPushButton(text)
    btn.setMinimumHeight(min_h)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: #6366f1; color: white; border: none;
            border-radius: 10px; font-size: 14px; font-weight: 600;
            padding: 10px 24px;
        }}
        QPushButton:hover {{ background: #4f46e5; }}
    """)
    return btn


def ghost_button(text):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background: transparent; color: #6366f1;
            border: 2px solid #e5e7eb; border-radius: 10px;
            padding: 8px 20px; font-size: 13px; font-weight: 600;
        }
        QPushButton:hover { border-color: #6366f1; background: #eef2ff; }
    """)
    return btn


class SectionHeader(QWidget):
    def __init__(self, title, refresh_callback=None):
        super().__init__()
        self.setObjectName("sectionHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)

        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        label.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(label)

        layout.addStretch()

        if refresh_callback:
            btn = ghost_button("+ Segarkan")
            btn.clicked.connect(refresh_callback)
            layout.addWidget(btn)


class CardContainer(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("cardItem")
        self.setGraphicsEffect(shadow())
        self.setStyleSheet("""
            QFrame#cardItem {
                background: #ffffff;
                border: none;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        self.card_layout = QVBoxLayout(scroll_content)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def clear(self):
        clear_layout(self.card_layout)


COMMON_STYLE = """
    QWidget {
        font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    }
    QWidget#contentBg {
        background: #f8fafc;
    }
    QFrame#cardItem {
        background: #ffffff;
        border: none;
        border-radius: 12px;
    }
    QLineEdit, QDateEdit {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 13px;
        background: #f9fafb;
    }
    QLineEdit:focus, QDateEdit:focus {
        border-color: #6366f1;
        background: #ffffff;
    }
    QDateEdit {
        padding: 8px 14px;
        min-height: 24px;
    }
    QComboBox {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 13px;
        background: #f9fafb;
        min-height: 20px;
    }
    QComboBox:focus {
        border-color: #6366f1;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 8px;
    }
    QComboBox QAbstractItemView {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        selection-background-color: #eef2ff;
        selection-color: #1f2937;
        padding: 4px;
    }
"""
