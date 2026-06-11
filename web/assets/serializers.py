from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Asset, Reservation

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer untuk JWT Token Obtain.
    Menambahkan claim 'role' dan 'username' ke dalam payload token.
    Ini mempermudah aplikasi desktop PySide6 untuk mengidentifikasi profil admin.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Menambahkan custom claim
        token['role'] = user.role
        token['username'] = user.username
        return token


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer untuk detail Custom User.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'first_name', 'last_name')


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer untuk pengelolaan Aset/Barang sekolah.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Asset
        fields = ('id', 'name', 'category', 'serial_number', 'status', 'status_display', 'description')


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer untuk Reservasi Aset yang digunakan oleh Peminjam maupun Admin.
    Memasukkan validasi bentrok tanggal (double-booking) melalui class method model.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    asset_detail = AssetSerializer(source='asset', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'id', 'user', 'user_detail', 'asset', 'asset_detail', 
            'start_date', 'end_date', 'status', 'status_display', 'admin_note'
        )
        read_only_fields = ('user', 'status', 'admin_note')

    def validate(self, attrs):
        """
        Validasi level serializer untuk memastikan tidak terjadi double-booking.
        Memanfaatkan Domain-Driven Design (Class Method pada model Reservation).
        """
        instance = self.instance
        
        # Ambil data input atau data yang sudah ada (jika partial update)
        asset = attrs.get('asset', getattr(instance, 'asset', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))
        exclude_id = instance.id if instance else None

        # 1. Pastikan tanggal mulai tidak mendahului tanggal selesai
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({
                    'start_date': "Tanggal mulai peminjaman tidak boleh melebihi tanggal selesai."
                })

            # 2. Hanya jalankan pengecekan overlap jika status reservasi aktif (misalnya saat pengajuan awal)
            current_status = getattr(instance, 'status', 'pending')
            if current_status in ['pending', 'approved', 'ongoing']:
                # Panggil class method dari model Reservation
                if Reservation.check_overlap(asset, start_date, end_date, exclude_id):
                    raise serializers.ValidationError(
                        "Maaf, aset/alat sekolah sudah dibooking oleh pengguna lain pada rentang tanggal yang Anda pilih."
                    )
        
        return attrs


class ReservationReviewSerializer(serializers.ModelSerializer):
    """
    Serializer khusus bagi Admin untuk menyetujui (Approve) atau menolak (Reject) peminjaman.
    Menerima status baru dan catatan (admin_note).
    """
    class Meta:
        model = Reservation
        fields = ('status', 'admin_note')
        extra_kwargs = {
            'status': {'required': True},
            'admin_note': {'required': True, 'allow_blank': False}
        }

    def validate_status(self, value):
        """
        Memastikan status yang dikirimkan oleh Admin hanya 'approved' atau 'rejected'.
        """
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Admin hanya dapat mengubah status menjadi 'approved' atau 'rejected'.")
        return value

    def update(self, instance, validated_data):
        """
        Melakukan update status reservasi.
        Jika disetujui (approved) dan tanggal mulai sama dengan hari ini, status bisa diatur.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.admin_note = validated_data.get('admin_note', instance.admin_note)
        instance.save()
        return instance
