from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Asset, Reservation
from .forms import ReservationForm

class PeminjamRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    [OOP - Inheritance]
    Mixin kustom untuk membatasi akses halaman web SSR hanya untuk pengguna
    yang memiliki role 'peminjam'. Pengguna 'admin' harus diarahkan kembali atau ditolak,
    karena admin menggunakan REST API dan aplikasi desktop PySide6.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'peminjam'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Logout admin jika mencoba masuk ke web app peminjam
            logout(self.request)
            messages.warning(
                self.request, 
                "Akun Admin terdeteksi! Admin hanya diperbolehkan mengakses via REST API Aplikasi Desktop."
            )
        return redirect('login')


class PeminjamLoginView(LoginView):
    """
    View untuk menangani halaman login peminjam.
    Menggunakan template login.html.
    """
    template_name = 'assets/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect ke katalog aset jika berhasil login
        return reverse_lazy('katalog')

    def form_invalid(self, form):
        messages.error(self.request, "Username atau password salah. Silakan coba lagi.")
        return super().form_invalid(form)


class PeminjamLogoutView(View):
    """
    View untuk menangani logout pengguna.
    Menggunakan Class-Based View (View utama).
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Anda telah berhasil logout.")
        return redirect('login')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Anda telah berhasil logout.")
        return redirect('login')


class AssetCatalogView(PeminjamRequiredMixin, ListView):
    """
    View katalog aset sekolah.
    Hanya menampilkan barang-barang yang statusnya 'available' (tersedia).
    """
    model = Asset
    template_name = 'assets/katalog.html'
    context_object_name = 'assets'

    def get_queryset(self):
        # Ambil filter kategori dari query string jika ada
        category_filter = self.request.GET.get('category')
        queryset = Asset.objects.filter(status='available')
        if category_filter:
            queryset = queryset.filter(category__iexact=category_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ambil semua kategori unik untuk filter di sidebar/nav
        context['categories'] = Asset.objects.filter(status='available').values_list('category', flat=True).distinct()
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ReservationCreateView(PeminjamRequiredMixin, CreateView):
    """
    View Form Booking / Pemesanan Aset.
    Menyimpan data dengan peminjam yang ter-login otomatis.
    """
    model = Reservation
    form_class = ReservationForm
    template_name = 'assets/booking.html'
    success_url = reverse_lazy('riwayat')

    def get_initial(self):
        """
        Jika peminjam menekan tombol booking dari katalog,
        maka aset akan langsung terpilih otomatis di Form Booking.
        """
        initial = super().get_initial()
        asset_id = self.request.GET.get('asset_id')
        if asset_id:
            try:
                asset = Asset.objects.get(id=asset_id, status='available')
                initial['asset'] = asset
            except Asset.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        """
        Mengisi field 'user' secara otomatis berdasarkan pengguna yang login,
        dan menetapkan status awal peminjaman menjadi 'pending'.
        """
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        
        # Validasi double-booking dilakukan di level model clean() via form.clean()
        try:
            messages.success(self.request, f"Pemesanan alat '{form.instance.asset.name}' berhasil diajukan! Menunggu persetujuan Admin.")
            return super().form_valid(form)
        except Exception as e:
            # Tangani jika validasi level model gagal (meski form biasanya menangani ValidationError)
            form.add_error(None, str(e))
            return self.form_invalid(form)


class ReservationHistoryView(PeminjamRequiredMixin, ListView):
    """
    View Riwayat Peminjaman milik user peminjam yang sedang login.
    Menampilkan daftar booking aktif dan masa lalu.
    """
    model = Reservation
    template_name = 'assets/riwayat.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Hanya tampilkan peminjaman milik user yang login saat ini
        return Reservation.objects.filter(user=self.request.user).select_related('asset')
