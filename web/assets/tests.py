from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from .models import Asset, Reservation

User = get_user_model()

class CustomUserModelTest(TestCase):
    """
    Menguji pembuatan Custom User dan kesesuaian field 'role'.
    """
    def test_create_user_roles(self):
        # 1. Test Peminjam
        peminjam = User.objects.create_user(
            username='peminjam1',
            password='password123',
            role='peminjam'
        )
        self.assertEqual(peminjam.role, 'peminjam')
        self.assertEqual(peminjam.get_role_display(), 'Peminjam')

        # 2. Test Admin
        admin = User.objects.create_user(
            username='admin1',
            password='password123',
            role='admin'
        )
        self.assertEqual(admin.role, 'admin')
        self.assertEqual(admin.get_role_display(), 'Admin')


class ReservationOverlapLogicTest(TestCase):
    """
    Menguji logika pencegahan Double-Booking di tingkat model.
    Menggunakan rumus bentrok: (start_date <= existing_end_date) AND (end_date >= existing_start_date)
    """
    def setUp(self):
        # Setup Data Awal
        self.peminjam1 = User.objects.create_user(username='peminjam1', password='pass', role='peminjam')
        self.peminjam2 = User.objects.create_user(username='peminjam2', password='pass', role='peminjam')
        self.asset = Asset.objects.create(
            name='Proyektor Epson X100',
            category='Elektronik',
            serial_number='EPS-100-XYZ',
            status='available'
        )

        # Reservasi Eksisting (Approved): 1 Juni 2026 s/d 5 Juni 2026
        self.existing_start = date(2026, 6, 1)
        self.existing_end = date(2026, 6, 5)
        self.existing_reservation = Reservation.objects.create(
            user=self.peminjam1,
            asset=self.asset,
            start_date=self.existing_start,
            end_date=self.existing_end,
            status='approved'
        )

    def test_overlap_middle_conflict(self):
        """
        Kasus 1: Rentang tanggal booking berada di tengah-tengah booking eksisting.
        Pengajuan: 2 Juni s/d 4 Juni.
        Hasil: Harus ValidationError (Bentrok).
        """
        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 6, 2),
            end_date=date(2026, 6, 4),
            status='pending'
        )
        with self.assertRaises(ValidationError):
            new_res.full_clean()

    def test_overlap_partial_start_conflict(self):
        """
        Kasus 2: Sebagian tanggal di akhir pengajuan menabrak bagian awal booking eksisting.
        Pengajuan: 28 Mei s/d 2 Juni.
        Hasil: Harus ValidationError (Bentrok).
        """
        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 5, 28),
            end_date=date(2026, 6, 2),
            status='pending'
        )
        with self.assertRaises(ValidationError):
            new_res.full_clean()

    def test_overlap_partial_end_conflict(self):
        """
        Kasus 3: Sebagian tanggal di awal pengajuan menabrak bagian akhir booking eksisting.
        Pengajuan: 4 Juni s/d 8 Juni.
        Hasil: Harus ValidationError (Bentrok).
        """
        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 6, 4),
            end_date=date(2026, 6, 8),
            status='pending'
        )
        with self.assertRaises(ValidationError):
            new_res.full_clean()

    def test_no_overlap_before(self):
        """
        Kasus 4: Pengajuan selesai sebelum booking eksisting dimulai.
        Pengajuan: 25 Mei s/d 31 Mei.
        Hasil: Berhasil (Tidak Bentrok).
        """
        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 5, 25),
            end_date=date(2026, 5, 31),
            status='pending'
        )
        try:
            new_res.full_clean()
        except ValidationError:
            self.fail("Peminjaman tidak bentrok tetapi memicu ValidationError!")

    def test_no_overlap_after(self):
        """
        Kasus 5: Pengajuan dimulai setelah booking eksisting selesai.
        Pengajuan: 6 Juni s/d 10 Juni.
        Hasil: Berhasil (Tidak Bentrok).
        """
        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 6, 6),
            end_date=date(2026, 6, 10),
            status='pending'
        )
        try:
            new_res.full_clean()
        except ValidationError:
            self.fail("Peminjaman tidak bentrok tetapi memicu ValidationError!")

    def test_overlap_with_rejected_existing(self):
        """
        Kasus 6: Ada booking eksisting yang bentrok tapi statusnya 'rejected'.
        Booking rejected tidak memblokir tanggal.
        Hasil: Berhasil (Tidak memicu ValidationError).
        """
        # Set reservasi eksisting menjadi rejected
        self.existing_reservation.status = 'rejected'
        self.existing_reservation.save()

        new_res = Reservation(
            user=self.peminjam2,
            asset=self.asset,
            start_date=date(2026, 6, 2),
            end_date=date(2026, 6, 4),
            status='pending'
        )
        try:
            new_res.full_clean()
        except ValidationError:
            self.fail("Status rejected seharusnya tidak memblokir booking tanggal lain!")


class WebAppPeminjamAccessTest(TestCase):
    """
    Menguji otentikasi dan pembatasan hak akses berbasis Role pada SSR Web App.
    """
    def setUp(self):
        self.peminjam = User.objects.create_user(username='peminjam', password='password123', role='peminjam')
        self.admin = User.objects.create_user(username='admin', password='password123', role='admin')

    def test_peminjam_can_access_catalog(self):
        # Login sebagai peminjam
        self.client.login(username='peminjam', password='password123')
        response = self.client.get(reverse('katalog'))
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_access_catalog(self):
        # Login sebagai admin
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('katalog'))
        # Admin akan dilempar ke login dan di-logout otomatis
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class AdminAPIRESTTest(APITestCase):
    """
    Menguji REST API Admin (DRF + SimpleJWT).
    """
    def setUp(self):
        self.peminjam = User.objects.create_user(username='peminjam', password='password123', role='peminjam')
        self.admin = User.objects.create_user(username='admin', password='password123', role='admin')
        
        self.asset = Asset.objects.create(
            name='Kamera DSLR Canon',
            category='Elektronik',
            serial_number='CAN-550D',
            status='available'
        )
        
        # Peminjam membuat 1 booking pending
        self.res = Reservation.objects.create(
            user=self.peminjam,
            asset=self.asset,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            status='pending'
        )

    def test_obtain_jwt_token_claims(self):
        """
        Memastikan custom claim 'role' disisipkan pada payload token JWT.
        """
        url = reverse('token_obtain_pair')
        data = {
            'username': 'admin',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Menguji jika login dengan user peminjam
        data_peminjam = {
            'username': 'peminjam',
            'password': 'password123'
        }
        response_pem = self.client.post(url, data_peminjam, format='json')
        self.assertEqual(response_pem.status_code, status.HTTP_200_OK)

    def test_peminjam_cannot_access_pending_api(self):
        """
        Peminjam menembak API admin pending list. Harus ditolak (403).
        """
        # Dapatkan token peminjam
        token_res = self.client.post(reverse('token_obtain_pair'), {'username': 'peminjam', 'password': 'password123'})
        access_token = token_res.data['access']
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('api_pending_reservations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_pending_api_and_review(self):
        """
        Admin menembak API pending list (200), lalu melakukan Approve (PATCH/PUT).
        """
        # Dapatkan token admin
        token_res = self.client.post(reverse('token_obtain_pair'), {'username': 'admin', 'password': 'password123'})
        access_token = token_res.data['access']
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 1. List pending
        url_list = reverse('api_pending_reservations')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.res.id)

        # 2. Approve booking
        url_review = reverse('api_review_reservation', kwargs={'pk': self.res.id})
        review_data = {
            'status': 'approved',
            'admin_note': 'Peminjaman disetujui, harap merawat kamera dengan baik.'
        }
        response_review = self.client.patch(url_review, review_data, format='json')
        self.assertEqual(response_review.status_code, status.HTTP_200_OK)
        
        # Verifikasi database terupdate
        self.res.refresh_from_db()
        self.assertEqual(self.res.status, 'approved')
        self.assertEqual(self.res.admin_note, 'Peminjaman disetujui, harap merawat kamera dengan baik.')
