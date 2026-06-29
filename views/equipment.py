from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFormLayout, QFrame, QComboBox, QMessageBox, QLineEdit, QDialog, QDialogButtonBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import DatabaseConnection
from views.widgets import shadow, clear_layout, action_button, primary_button, ghost_button, CardContainer, COMMON_STYLE


class DialogEditBarang(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Edit Barang")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_nama = QLineEdit(data.get("nama_barang", ""))
        self.input_nama.setMinimumHeight(40)
        form.addRow("Nama Barang:", self.input_nama)

        self.input_kategori = QComboBox()
        self.input_kategori.setMinimumHeight(40)
        self.input_kategori.addItems(["Kamera", "Lighting", "Stabilizer", "Audio", "Lainnya"])
        idx = self.input_kategori.findText(data.get("kategori", ""))
        if idx >= 0:
            self.input_kategori.setCurrentIndex(idx)
        form.addRow("Kategori:", self.input_kategori)

        self.input_sn = QLineEdit(data.get("serial_number", ""))
        self.input_sn.setMinimumHeight(40)
        form.addRow("Serial Number:", self.input_sn)

        self.input_stok = QLineEdit(str(data.get("stock", "")))
        self.input_stok.setMinimumHeight(40)
        form.addRow("Stok:", self.input_stok)

        self.input_deskripsi = QLineEdit(data.get("description", "") or "")
        self.input_deskripsi.setMinimumHeight(40)
        form.addRow("Deskripsi:", self.input_deskripsi)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setStyleSheet(COMMON_STYLE)

    def get_data(self):
        return {
            "nama_barang": self.input_nama.text().strip(),
            "kategori": self.input_kategori.currentText(),
            "serial_number": self.input_sn.text().strip(),
            "stock": self.input_stok.text().strip(),
            "description": self.input_deskripsi.text().strip(),
        }


class TampilanDaftarBarang(QWidget):
    def __init__(self):
        super().__init__()
        self.items = []
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Daftar Barang")
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
        self.items = DatabaseConnection().get_all_equipment()
        self.container.clear()
        for item in self.items:
            self.container.card_layout.addWidget(self._card(item))

    def _card(self, item):
        card = QFrame()
        card.setObjectName("barangCard")
        card.setFixedHeight(60)
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(12)

        info = QVBoxLayout()
        info.setSpacing(0)
        nama = QLabel(item.get("nama_barang", ""))
        nama.setFont(QFont("Segoe UI", 13, QFont.Bold))
        nama.setStyleSheet("color: #1f2937; border: none; background: transparent;")
        info.addWidget(nama)
        sub = QLabel(f"{item.get('kategori', '')} \u2022 {item.get('serial_number', '')} \u2022 Stok: {item.get('stock', '')}")
        sub.setStyleSheet("color: #6b7280; font-size: 12px; border: none; background: transparent;")
        info.addWidget(sub)
        row.addLayout(info, 1)

        btn_edit = action_button("Edit", "#6366f1", "#4f46e5", (68, 30))
        btn_edit.clicked.connect(lambda checked, i=item: self.edit_item(i))
        row.addWidget(btn_edit)

        btn_hapus = action_button("Hapus", "#ef4444", "#dc2626", (68, 30))
        btn_hapus.clicked.connect(lambda checked, i=item: self.delete_item(i))
        row.addWidget(btn_hapus)

        card.setStyleSheet("""
            QFrame#barangCard {
                background: transparent;
                border-bottom: 1px solid #f3f4f6;
            }
            QFrame#barangCard:hover {
                background: #f8fafc;
            }
        """)
        return card

    def edit_item(self, item):
        dialog = DialogEditBarang(item)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not all([data["nama_barang"], data["serial_number"], data["stock"]]):
                QMessageBox.warning(self, "Error", "Field wajib diisi.")
                return
            db = DatabaseConnection()
            ok = db.update_equipment(item["id"], data["nama_barang"], data["kategori"], data["serial_number"], int(data["stock"]), data["description"])
            QMessageBox.information(self, "Sukses", "Barang berhasil diperbarui.") if ok else QMessageBox.warning(self, "Error", "Gagal memperbarui barang.")
            if ok:
                self.load_data()

    def delete_item(self, item):
        confirm = QMessageBox.question(self, "Konfirmasi Hapus", f"Hapus barang '{item['nama_barang']}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            ok = DatabaseConnection().delete_equipment(item["id"])
            QMessageBox.information(self, "Sukses", "Barang berhasil dihapus.") if ok else QMessageBox.warning(self, "Error", "Gagal menghapus barang.")
            if ok:
                self.load_data()


class TampilanTambahBarang(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("contentBg")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)

        header = QLabel("Tambah Barang Baru")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(header)

        desc = QLabel("Lengkapi data di bawah untuk menambahkan barang ke inventaris.")
        desc.setStyleSheet("color: #6b7280; border: none; font-size: 13px; margin-bottom: 16px;")
        layout.addWidget(desc)

        form_card = QFrame()
        form_card.setObjectName("cardItem")
        form_card.setGraphicsEffect(shadow())
        fc = QVBoxLayout(form_card)
        fc.setContentsMargins(28, 28, 28, 28)
        fc.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.input_nama = QLineEdit()
        self.input_nama.setMinimumHeight(42)
        self.input_nama.setPlaceholderText("Masukkan nama barang")
        form.addRow("Nama Barang:", self.input_nama)

        self.input_kategori = QComboBox()
        self.input_kategori.setMinimumHeight(42)
        self.input_kategori.addItems(["Kamera", "Lighting", "Stabilizer", "Audio", "Lainnya"])
        form.addRow("Kategori:", self.input_kategori)

        self.input_sn = QLineEdit()
        self.input_sn.setMinimumHeight(42)
        self.input_sn.setPlaceholderText("Masukkan serial number")
        form.addRow("Serial Number:", self.input_sn)

        self.input_stok = QLineEdit()
        self.input_stok.setMinimumHeight(42)
        self.input_stok.setPlaceholderText("0")
        form.addRow("Stok:", self.input_stok)

        self.input_deskripsi = QLineEdit()
        self.input_deskripsi.setMinimumHeight(42)
        self.input_deskripsi.setPlaceholderText("Deskripsi opsional")
        form.addRow("Deskripsi:", self.input_deskripsi)

        fc.addLayout(form)

        br = QHBoxLayout()
        br.addStretch()
        btn = primary_button("Simpan Barang")
        btn.clicked.connect(self.handle_save)
        br.addWidget(btn)
        fc.addLayout(br)

        layout.addWidget(form_card)
        layout.addStretch()

    def handle_save(self):
        nama = self.input_nama.text().strip()
        kategori = self.input_kategori.currentText()
        sn = self.input_sn.text().strip()
        stok = self.input_stok.text().strip()
        if not all([nama, sn, stok]):
            QMessageBox.warning(self, "Error", "Field wajib diisi.")
            return
        ok = DatabaseConnection().add_equipment(nama, kategori, sn, int(stok), self.input_deskripsi.text())
        if ok:
            QMessageBox.information(self, "Sukses", "Berhasil disimpan!")
            for w in [self.input_nama, self.input_sn, self.input_stok, self.input_deskripsi]:
                w.clear()
        else:
            QMessageBox.warning(self, "Error", "Gagal menyimpan.")
