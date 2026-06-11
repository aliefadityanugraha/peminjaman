from django.contrib import admin
from .models import Asset, Reservation

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'serial_number', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name', 'serial_number', 'category')
    ordering = ('name',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'asset', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'asset__name', 'asset__serial_number')
    ordering = ('-start_date',)
    readonly_fields = ('id',)
