-- 1. Membuat Database
CREATE DATABASE IF NOT EXISTS pf_spaces;
USE pf_spaces;

-- Hapus tabel lama jika ada (untuk menghindari error saat reset data)
DROP TABLE IF EXISTS reservasi;
DROP TABLE IF EXISTS barang;
DROP TABLE IF EXISTS info_barang;
DROP TABLE IF EXISTS user;

-- ==========================================
-- 2. MEMBUAT TABEL-TABEL UTAMA
-- ==========================================

-- Tabel: user
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Di produksi nyata wajib di-hash
    role ENUM('admin', 'peminjam') NOT NULL,
    no_hp VARCHAR(15)
);

-- Tabel: info_barang (Dibuat duluan karena akan direferensikan oleh tabel barang)
CREATE TABLE info_barang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tahun_beli INT,
    panduan TEXT
);

-- Tabel: barang
CREATE TABLE barang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_barang VARCHAR(100) NOT NULL,
    kategori VARCHAR(50),
    serial_number VARCHAR(50) UNIQUE,
    stock INT DEFAULT 1,
    description TEXT,
    info_id INT,
    FOREIGN KEY (info_id) REFERENCES info_barang(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabel: reservasi
CREATE TABLE reservasi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'returned') DEFAULT 'pending',
    admin_note TEXT,
    user_id INT,
    barang_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- ==========================================
-- 3. MENGISI DATA AWAL (DUMMY DATA)
-- ==========================================

-- Mengisi Data User (1 Admin & 3 Anggota Kelompok sebagai Peminjam)
INSERT INTO user (email, username, password, role, no_hp) VALUES
('admin.film@school.sch.id', 'admin', 'admin123', 'admin', '081234567890'),
('misbach.hafit@student.id', 'misbach', 'peminjam123', 'peminjam', '085711112222'),
('alief.aditya@student.id', 'alief', 'peminjam123', 'peminjam', '085733334444'),
('todo.haris@student.id', 'todo', 'peminjam123', 'peminjam', '085755556666');

-- Mengisi Data Info Barang (Panduan & Detail Teknis)
INSERT INTO info_barang (tahun_beli, panduan) VALUES
(2024, 'SOP: Pastikan pelindung lensa terpasang saat tidak merekam. Jangan mengganti lensa di tempat berdebu. Video edukasi: https://link-panduan.com/sony-a7iv'),
(2023, 'SOP: Gunakan baterai V-Mount yang terisi penuh. Jangan menyentuh manik lampu COB secara langsung. Panduan: PDF-Amaran200d.pdf'),
(2025, 'SOP: Jangan memaksa motor stabilizer sebelum diseimbangkan (balancing) secara manual. Video tutorial: https://link-panduan.com/ronin-sc'),
(2024, 'SOP: Matikan switch phantom power 48V sebelum mencabut kabel XLR untuk menghindari lonjakan tegangan.');

-- Mengisi Data Barang (Aset Alat Produksi Film)
INSERT INTO barang (nama_barang, kategori, serial_number, stock, description, info_id) VALUES
('Kamera Sony Alpha 7 IV Body Only', 'Kamera', 'SN-SONY-A7IV-01', 1, 'Kamera mirrorless hybrid full-frame untuk kebutuhan sinematografi tingkat lanjut.', 1),
('Lighting Aputure Amaran 200d LED Continuous Light', 'Lighting', 'SN-APUT-200D-05', 2, 'Lampu LED output daya tinggi 200W untuk pencahayaan studio/lokasi.', 2),
('DJI Ronin-SC 3-Axis Gimbal Stabilizer', 'Stabilizer', 'SN-DJI-RSC-12', 1, 'Stabilizer kamera tiga sumbu untuk pergerakan video yang mulus.', 3),
('Microphone Rode VideoMic Pro+', 'Audio', 'SN-RODE-VMP-09', 3, 'Shotgun microphone on-camera untuk perekaman audio eksternal yang jernih.', 4);

-- Mengisi Data Riwayat Reservasi Awal untuk Testing Aplikasi
INSERT INTO reservasi (start_date, end_date, status, admin_note, user_id, barang_id) VALUES
('2026-06-24', '2026-06-26', 'pending', NULL, 2, 1),   -- Misbach ingin pinjam Sony A7IV (Perlu konfirmasi admin)
('2026-06-25', '2026-06-25', 'pending', NULL, 3, 2),   -- Alief ingin pinjam Lighting Amaran (Perlu konfirmasi admin)
('2026-06-20', '2026-06-22', 'returned', 'Alat kembali dalam keadaan bersih dan lengkap.', 4, 3); -- Todo sudah selesai pinjam DJI Ronin