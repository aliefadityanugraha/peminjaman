# Pf Spaces

Aplikasi manajemen peminjaman perlengkapan produksi film berbasis **PySide6** (desktop) dan **Django** (web).

## Fitur

### Role Admin
- CRUD barang inventaris (tambah, edit, hapus)
- Menyetujui atau menolak permintaan peminjaman
- Melihat daftar reservasi yang menunggu konfirmasi

### Role Peminjam
- Melihat daftar barang tersedia dan tidak tersedia
- Mengajukan permintaan peminjaman barang
- Melihat riwayat peminjaman pribadi

## Tech Stack

| Layer   | Teknologi                                |
| ------- | ---------------------------------------- |
| Desktop | Python, PySide6, MySQL Connector         |
| Web     | Django, Django REST Framework            |
| Database| MySQL                                    |

## Struktur Folder

```
pyside/              # Aplikasi desktop utama
├── main.py          # Entry point
├── database.py      # Koneksi & query MySQL
├── model/           # Class model (User, Barang, Reservasi)
└── views/           # Tampilan GUI
    ├── login.py     # Halaman login
    ├── admin.py     # Dashboard admin
    ├── peminjam.py  # Dashboard peminjam
    ├── navbar.py    # Navigasi bar (reusable)
    ├── widgets.py   # Komponen UI bersama
    ├── equipment.py # CRUD barang
    └── reservation.py # Konfirmasi reservasi

web/                 # Aplikasi web Django
└── ...
```

## Setup Database

1. Pastikan MySQL sudah berjalan
2. Jalankan script inisialisasi:

```bash
mysql -u root < pyside/peminjaman.sql
```

Script ini akan membuat database `peminjaman` dan mengisi data dummy.

## Menjalankan App Desktop

```bash
cd pyside
pip install -r requirements.txt  # atau: PySide6 mysql-connector-python
python main.py
```

Akun dummy yang tersedia:

| Username  | Password      | Role    |
| --------- | ------------- | ------- |
| admin     | admin123      | admin   |
| misbach   | peminjam123   | peminjam|
| alief     | peminjam123   | peminjam|
| todo      | peminjam123   | peminjam|

## Mode Offline

Jika MySQL tidak tersambung, gunakan kredensial `admin / admin` untuk login offline.
