class User:
    def __init__(self, id, email, username, password, role, no_hp):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.role = role
        self.no_hp = no_hp
        self.reservasi = []


class Barang:
    def __init__(self, id, nama_barang, kategori, serial_number, stock, description, info_id):
        self.id = id
        self.nama_barang = nama_barang
        self.kategori = kategori
        self.serial_number = serial_number
        self.stock = stock
        self.description = description
        self.info_id = info_id
        self.reservasi = []


class Reservasi:
    def __init__(self, id, start_date, end_date, status, admin_note, user_id, barang_id):
        self.id = id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.admin_note = admin_note
        self.user_id = user_id
        self.barang_id = barang_id


class InfoBarang:
    def __init__(self, id, tahun_beli, panduan):
        self.id = id
        self.tahun_beli = tahun_beli
        self.panduan = panduan

# info_laptop = InfoBarang(id=1, tahun_beli=2025, panduan="Panduan Penggunaan")
# laptop = Barang(id=101, nama_barang="Laptop ASUS", kategori="Elektronik", serial_number="SN12345", stock=5, description="Laptop Core i7", info_id=info_laptop.id)

# user_baru = User(id=1, email="budi@email.com", username="budi99", password="123", role="member", no_hp="0812345678")

# reservasi_budi = Reservasi(id=501, start_date="2026-06-11", end_date="2026-06-15", status="Diproses", admin_note="Harap bawa KTP", user_id=user_baru.id, barang_id=laptop.id)

# user_baru.reservasi.append(reservasi_budi)
# laptop.reservasi.append(reservasi_budi)

# print(f"User {user_baru.username} membuat reservasi untuk barang ID: {reservasi_budi.barang_id}")