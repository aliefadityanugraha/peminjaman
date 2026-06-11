from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Asset(models.Model):
    """
    Model Asset mewakili barang atau alat sekolah yang dapat dipinjam.
    Aplikasi ini gratis/untuk peminjaman internal, sehingga tidak ada nominal harga.
    """
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('maintenance', 'Maintenance'),
        ('broken', 'Broken'),
    )

    name = models.CharField(max_length=255, help_text="Nama barang / alat sekolah")
    category = models.CharField(max_length=100, help_text="Kategori barang (misal: Elektronik, Olahraga, Seni)")
    serial_number = models.CharField(max_length=100, unique=True, help_text="Nomor seri unik barang")
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='available',
        help_text="Status ketersediaan barang"
    )
    description = models.TextField(blank=True, null=True, help_text="Deskripsi kondisi atau detail barang")

    def __str__(self):
        return f"{self.name} ({self.serial_number}) - {self.get_status_display()}"


class Reservation(models.Model):
    """
    Model Reservation mewakili pemesanan/booking aset oleh peminjam.
    Diatur agar tidak terjadi double-booking pada rentang tanggal yang bentrok.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="User peminjam aset"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Aset yang dipinjam"
    )
    start_date = models.DateField(help_text="Tanggal mulai peminjaman")
    end_date = models.DateField(help_text="Tanggal selesai peminjaman")
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status persetujuan peminjaman oleh Admin"
    )
    admin_note = models.TextField(
        blank=True,
        null=True,
        help_text="Catatan peninjauan dari Admin (misal: Alasan Reject/Approve)"
    )

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Reservation #{self.id} | {self.user.username} - {self.asset.name} ({self.start_date} s/d {self.end_date})"

    @classmethod
    def check_overlap(cls, asset, start_date, end_date, exclude_reservation_id=None):
        """
        [Domain-Driven Design - Class Method]
        Mengecek apakah terdapat reservasi lain untuk aset yang sama pada rentang tanggal yang bentrok.
        
        Rumus Bentrok: (start_date <= existing_end_date) AND (end_date >= existing_start_date)
        
        Hanya reservasi yang berstatus 'approved', 'ongoing', atau 'pending' yang dianggap memicu bentrok.
        Reservasi berstatus 'rejected' atau 'completed' tidak memblokir tanggal.
        """
        if not asset or not start_date or not end_date:
            return False

        # Query filter untuk mencari reservasi yang bentrok
        overlapping_query = cls.objects.filter(
            asset=asset,
            status__in=['pending', 'approved', 'ongoing'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        # Jika sedang melakukan pembaruan (update) reservasi, kecualikan id objek ini agar tidak bentrok dengan dirinya sendiri
        if exclude_reservation_id:
            overlapping_query = overlapping_query.exclude(id=exclude_reservation_id)

        return overlapping_query.exists()

    def clean(self):
        """
        Validasi level model sebelum penyimpanan data.
        """
        super().clean()

        if self.start_date and self.end_date:
            # 1. Validasi urutan tanggal
            if self.start_date > self.end_date:
                raise ValidationError({
                    'start_date': "Tanggal mulai peminjaman tidak boleh melebihi tanggal selesai."
                })

            # 2. Validasi status aset harus available (hanya saat booking baru bertipe pending/approved)
            # Reservasi baru tidak boleh dilakukan jika aset berstatus maintenance atau broken.
            if not self.pk and self.asset.status != 'available':
                raise ValidationError({
                    'asset': f"Aset '{self.asset.name}' saat ini tidak dapat dipinjam karena berstatus '{self.asset.get_status_display()}'."
                })

            # 3. Validasi double-booking menggunakan enkapsulasi logika di class method
            # Pengecekan hanya relevan jika reservasi yang diajukan berstatus aktif (pending, approved, ongoing)
            if self.status in ['pending', 'approved', 'ongoing']:
                if self.check_overlap(self.asset, self.start_date, self.end_date, self.id):
                    raise ValidationError(
                        "Maaf, aset/alat sekolah sudah dibooking oleh pengguna lain pada rentang tanggal yang Anda pilih."
                    )

    def save(self, *args, **kwargs):
        """
        Override save untuk memastikan clean() selalu dijalankan sebelum menyimpan ke database,
        menjaga integritas data baik via Admin Django, Web View, maupun API.
        """
        self.full_clean()
        super().save(*args, **kwargs)
