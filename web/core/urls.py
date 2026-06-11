"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import views Web App Peminjam
from assets.views import (
    PeminjamLoginView,
    PeminjamLogoutView,
    AssetCatalogView,
    ReservationCreateView,
    ReservationHistoryView,
)

# Import views REST API Admin
from assets.api_views import (
    PendingReservationsAPIView,
    ReviewReservationAPIView,
)

urlpatterns = [
    # Admin Panel Django (bawaan)
    path('django-admin/', admin.site.urls),

    # ==================== SSR WEB APP (PEMINJAM) ====================
    path('', RedirectView.as_view(url='katalog/', permanent=False), name='home'),
    path('login/', PeminjamLoginView.as_view(), name='login'),
    path('logout/', PeminjamLogoutView.as_view(), name='logout'),
    path('katalog/', AssetCatalogView.as_view(), name='katalog'),
    path('booking/', ReservationCreateView.as_view(), name='booking'),
    path('riwayat/', ReservationHistoryView.as_view(), name='riwayat'),

    # ==================== REST API DRF (ADMIN) ====================
    # Autentikasi API SimpleJWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Endpoints khusus Admin (Akan dikonsumsi oleh desktop PySide6)
    path('api/admin/reservations/pending/', PendingReservationsAPIView.as_view(), name='api_pending_reservations'),
    path('api/admin/reservations/<int:pk>/review/', ReviewReservationAPIView.as_view(), name='api_review_reservation'),
]
