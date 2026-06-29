from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Signal
from views.navbar import Navbar, NAVBAR_STYLE
from views.equipment import TampilanDaftarBarang, TampilanTambahBarang
from views.reservation import TampilanKonfirmasiReservasi
from views.widgets import COMMON_STYLE


class DashboardAdmin(QWidget):
    logout_requested = Signal()

    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Pf Spaces \u2014 Admin")
        self.resize(1100, 720)
        self.setMinimumSize(900, 550)

        nav_items = [
            ("btn_daftar", "Daftar Barang", 0),
            ("btn_tambah", "Tambah Barang", 1),
            ("btn_reservasi", "Reservasi", 2),
        ]
        role_text = f"{user.role.title()} \u2022 {user.email}" if user else "Admin"

        self.navbar = Navbar("Pf Spaces", role_text, user.username if user else None, nav_items)
        self.navbar.page_changed.connect(self.switch_page)
        self.navbar.logout_clicked.connect(self.logout_requested.emit)

        self.stack = QStackedWidget()
        self.stack.addWidget(TampilanDaftarBarang())
        self.stack.addWidget(TampilanTambahBarang())
        self.stack.addWidget(TampilanKonfirmasiReservasi())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.navbar)
        layout.addWidget(self.stack, 1)

        self.setStyleSheet(NAVBAR_STYLE + COMMON_STYLE)
        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        self.navbar.set_active(index)
