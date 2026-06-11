from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom User Model yang menggantikan User default Django.
    Memiliki field 'role' untuk membedakan antara 'admin' (pengelola)
    dan 'peminjam' (peminjam aset/alat sekolah).
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('peminjam', 'Peminjam'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='peminjam',
        help_text="Role pengguna: 'admin' untuk Admin API, 'peminjam' untuk SSR Web App."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
