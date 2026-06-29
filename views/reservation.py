from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import DatabaseConnection
from views.widgets import shadow, action_button, ghost_button, CardContainer


class TampilanKonfirmasiReservasi(QWidget):
    def __init__(self):
        super().__init__()
        self.reservations = []
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Reservasi Menunggu")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1f2937; border: none;")
        hr = QHBoxLayout()
        hr.addWidget(header)
        hr.addStretch()
        btn = ghost_button("+ Segarkan")
        btn.clicked.connect(self.load_data)
        hr.addWidget(btn)
        layout.addLayout(hr)

        self.container = CardContainer()
        layout.addWidget(self.container)
        self.load_data()

    def load_data(self):
        self.reservations = DatabaseConnection().get_pending_reservations()
        self.container.clear()
        for r in self.reservations:
            self.container.card_layout.addWidget(self._card(r))

    def _card(self, r):
        card = QFrame()
        card.setObjectName("reservasiCard")
        card.setFixedHeight(60)
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(12)

        info = QVBoxLayout()
        info.setSpacing(0)
        title = QLabel(f"Reservasi #{r.get('id', '')}")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none; background: transparent;")
        info.addWidget(title)
        sub = QLabel(f"User: {r.get('user_id', '')} \u2022 Barang: {r.get('barang_id', '')} \u2022 {r.get('start_date', '')} \u2013 {r.get('end_date', '')}")
        sub.setStyleSheet("color: #6b7280; font-size: 12px; border: none; background: transparent;")
        info.addWidget(sub)
        row.addLayout(info, 1)

        btn_setujui = action_button("Setujui", "#22c55e", "#16a34a", (76, 30))
        btn_setujui.clicked.connect(lambda checked, x=r: self.approve(x))
        row.addWidget(btn_setujui)

        btn_tolak = action_button("Tolak", "#ef4444", "#dc2626", (76, 30))
        btn_tolak.clicked.connect(lambda checked, x=r: self.reject(x))
        row.addWidget(btn_tolak)

        card.setStyleSheet("""
            QFrame#reservasiCard {
                background: transparent;
                border-bottom: 1px solid #f3f4f6;
            }
            QFrame#reservasiCard:hover {
                background: #f8fafc;
            }
        """)
        return card

    def approve(self, r):
        if QMessageBox.question(self, "Konfirmasi", f"Setujui reservasi ID #{r['id']}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            ok = DatabaseConnection().approve_reservation(r["id"])
            QMessageBox.information(self, "Sukses", "Reservasi disetujui.") if ok else QMessageBox.warning(self, "Error", "Gagal menyetujui.")
            if ok:
                self.load_data()

    def reject(self, r):
        if QMessageBox.question(self, "Konfirmasi", f"Tolak reservasi ID #{r['id']}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            ok = DatabaseConnection().reject_reservation(r["id"])
            QMessageBox.information(self, "Sukses", "Reservasi ditolak.") if ok else QMessageBox.warning(self, "Error", "Gagal menolak.")
            if ok:
                self.load_data()
