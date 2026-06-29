from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox, QDateEdit, QStackedWidget, QScrollArea
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from database import DatabaseConnection
from views.navbar import Navbar, NAVBAR_STYLE
from views.widgets import shadow, clear_layout, status_badge, primary_button, COMMON_STYLE


class DashboardPeminjam(QWidget):
    logout_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Pf Spaces — Peminjam")
        self.resize(1100, 720)
        self.setMinimumSize(900, 550)

        nav_items = [
            ("btn_daftar", "Daftar Barang", 0),
            ("btn_pinjam", "Ajukan Peminjaman", 1),
            ("btn_history", "Riwayat Saya", 2),
        ]
        role_text = f"{user.role.title()} \u2022 {user.email}" if user else "Peminjam"

        self.navbar = Navbar("Pf Spaces", role_text, user.username if user else None, nav_items)
        self.navbar.page_changed.connect(self.switch_page)
        self.navbar.logout_clicked.connect(self.logout_requested.emit)

        self.stack = QStackedWidget()
        self.daftar_page = _DaftarBarang()
        self.pinjam_page = _AjukanPeminjaman(self.user.id)
        self.history_page = _RiwayatPeminjaman(self.user.id)
        self.stack.addWidget(self.daftar_page)
        self.stack.addWidget(self.pinjam_page)
        self.stack.addWidget(self.history_page)

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
        if index == 1:
            self.pinjam_page.refresh()
        if index == 2:
            self.history_page.refresh()


class _DaftarBarang(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Daftar Barang")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(header)

        desc = QLabel("Lihat ketersediaan barang inventaris.")
        desc.setStyleSheet("color: #6b7280; border: none; font-size: 13px; margin-bottom: 12px;")
        layout.addWidget(desc)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        self.card_layout = QVBoxLayout(scroll_content)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(10)
        self.card_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.refresh()

    def refresh(self):
        clear_layout(self.card_layout)
        db = DatabaseConnection()
        available = db.get_available_barang()
        unavailable = db.get_unavailable_barang()

        if not available and not unavailable:
            empty = QLabel("Belum ada barang di inventaris.")
            empty.setStyleSheet("color: #9ca3af; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.card_layout.addWidget(empty)
            return

        for items, label_text, color, bg in [
            (available, "Tersedia", "#16a34a", "#f0fdf4"),
            (unavailable, "Stok Habis", "#dc2626", "#fef2f2"),
        ]:
            if not items:
                continue
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 11, QFont.Bold))
            label.setStyleSheet(f"color: {color}; border: none; margin: 4px 4px 0 4px;")
            self.card_layout.addWidget(label)
            for item in items:
                self.card_layout.addWidget(self._card(item, label_text == "Tersedia"))

    def _card(self, item, available):
        card = QFrame()
        card.setObjectName("cardItem")
        card.setMinimumHeight(68)
        card.setGraphicsEffect(shadow())
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 14, 20, 14)

        info = QVBoxLayout()
        info.setSpacing(2)
        nama = QLabel(item.get("nama_barang", ""))
        nama.setFont(QFont("Segoe UI", 13, QFont.Bold))
        nama.setStyleSheet("color: #1f2937; border: none;")
        info.addWidget(nama)
        sub = QLabel(f"{item.get('kategori', '')} \u2022 SN: {item.get('serial_number', '')} \u2022 Stok: {item.get('stock', 0)}")
        sub.setStyleSheet("color: #6b7280; font-size: 12px; border: none;")
        info.addWidget(sub)
        row.addLayout(info, 1)
        row.addWidget(status_badge("Tersedia" if available else "Stok Habis", "#16a34a" if available else "#dc2626", "#f0fdf4" if available else "#fef2f2"))
        return card


class _AjukanPeminjaman(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Ajukan Peminjaman")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(header)

        desc = QLabel("Pilih barang dan tentukan tanggal peminjaman.")
        desc.setStyleSheet("color: #6b7280; border: none; font-size: 13px; margin-bottom: 16px;")
        layout.addWidget(desc)

        form_card = QFrame()
        form_card.setObjectName("cardItem")
        form_card.setMinimumWidth(500)
        form_card.setGraphicsEffect(shadow())
        fc = QVBoxLayout(form_card)
        fc.setContentsMargins(28, 28, 28, 28)
        fc.setSpacing(16)

        fc.addWidget(QLabel("Pilih Barang:"))
        self.combo = _BarangSelector()
        fc.addWidget(self.combo)

        dr = QHBoxLayout()
        dr.setSpacing(16)
        for label_text, attr, default_offset, min_offset in [
            ("Tanggal Mulai:", "mulai", 0, 0),
            ("Tanggal Selesai:", "selesai", 1, 1),
        ]:
            vb = QVBoxLayout()
            vb.addWidget(QLabel(label_text))
            editor = QDateEdit()
            editor.setCalendarPopup(True)
            editor.setDate(QDate.currentDate().addDays(default_offset))
            editor.setMinimumDate(QDate.currentDate().addDays(min_offset))
            editor.setMinimumHeight(40)
            setattr(self, f"tgl_{attr}", editor)
            vb.addWidget(editor)
            dr.addLayout(vb)
        fc.addLayout(dr)

        br = QHBoxLayout()
        br.addStretch()
        btn = primary_button("Ajukan Peminjaman", 200)
        btn.clicked.connect(self._submit)
        br.addWidget(btn)
        fc.addLayout(br)

        layout.addWidget(form_card)
        layout.addStretch()

    def refresh(self):
        self.combo.refresh()

    def _submit(self):
        barang = self.combo.selected()
        if not barang:
            QMessageBox.warning(self, "Error", "Pilih barang terlebih dahulu.")
            return
        mulai = self.tgl_mulai.date().toPython()
        selesai = self.tgl_selesai.date().toPython()
        if selesai <= mulai:
            QMessageBox.warning(self, "Error", "Tanggal selesai harus setelah tanggal mulai.")
            return
        ok = DatabaseConnection().add_reservation(self.user_id, barang["id"], mulai, selesai)
        if ok:
            QMessageBox.information(self, "Sukses", "Peminjaman diajukan, menunggu persetujuan admin.")
            self.combo.refresh()
        else:
            QMessageBox.warning(self, "Error", "Gagal mengajukan peminjaman.")


class _BarangSelector(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("cardItem")
        self._items = []
        self._sel = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        self.label = QLabel("Klik untuk memilih barang...")
        self.label.setStyleSheet("color: #6b7280; font-size: 13px; border: none;")
        layout.addWidget(self.label, 1)
        self.refresh()

    def selected(self):
        return self._sel

    def refresh(self):
        self._items = DatabaseConnection().get_available_barang()
        self._sel = self._items[0] if self._items else None
        self.label.setText(self._sel["nama_barang"] if self._sel else "Tidak ada barang tersedia")

    def mousePressEvent(self, event):
        if not self._items:
            return
        names = [it["nama_barang"] for it in self._items]
        msg = QMessageBox(self)
        msg.setWindowTitle("Pilih Barang")
        msg.setText("\n".join(f"{i+1}. {n}" for i, n in enumerate(names)))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("Pilih Selanjutnya")
        idx = 0
        if self._sel:
            for i, it in enumerate(self._items):
                if it["id"] == self._sel["id"]:
                    idx = (i + 1) % len(self._items)
                    break
        self._sel = self._items[idx]
        self.label.setText(self._sel["nama_barang"])


class _RiwayatPeminjaman(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Riwayat Peminjaman Saya")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        self.card_layout = QVBoxLayout(scroll_content)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(8)
        self.card_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.refresh()

    def refresh(self):
        clear_layout(self.card_layout)
        items = DatabaseConnection().get_reservations_by_user(self.user_id)
        if not items:
            empty = QLabel("Belum ada riwayat peminjaman.")
            empty.setStyleSheet("color: #9ca3af; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.card_layout.addWidget(empty)
            return
        for item in items:
            self.card_layout.addWidget(self._card(item))

    def _card(self, item):
        card = QFrame()
        card.setObjectName("cardItem")
        card.setMinimumHeight(68)
        card.setGraphicsEffect(shadow())
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 14, 20, 14)

        info = QVBoxLayout()
        info.setSpacing(2)
        nama = QLabel(item.get("nama_barang", f"Barang #{item.get('barang_id', '')}"))
        nama.setFont(QFont("Segoe UI", 13, QFont.Bold))
        nama.setStyleSheet("color: #1f2937; border: none;")
        info.addWidget(nama)
        sub = QLabel(f"{item.get('start_date', '')} \u2013 {item.get('end_date', '')}")
        sub.setStyleSheet("color: #6b7280; font-size: 12px; border: none;")
        info.addWidget(sub)
        row.addLayout(info, 1)

        sm = {
            "pending": ("Menunggu", "#f59e0b", "#fffbeb"),
            "approved": ("Disetujui", "#16a34a", "#f0fdf4"),
            "rejected": ("Ditolak", "#dc2626", "#fef2f2"),
            "returned": ("Dikembalikan", "#6366f1", "#eef2ff"),
        }
        label, color, bg = sm.get(item.get("status", ""), ("Unknown", "#6b7280", "#f3f4f6"))
        row.addWidget(status_badge(label, color, bg))
        return card
