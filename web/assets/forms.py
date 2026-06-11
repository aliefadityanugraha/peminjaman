from django import forms
from django.core.exceptions import ValidationError
from .models import Reservation, Asset


class ReservationForm(forms.ModelForm):
    """
    Form untuk melakukan booking aset sekolah oleh peminjam.
    Menggunakan HTML5 date picker untuk input rentang tanggal.
    """
    class Meta:
        model = Reservation
        fields = ['asset', 'start_date', 'end_date']
        widgets = {
            'asset': forms.Select(attrs={
                'class': 'form-select form-select-lg border-2 bg-dark-subtle text-light',
                'style': 'border-color: rgba(255,255,255,0.1);'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg border-2 bg-dark-subtle text-light',
                'style': 'border-color: rgba(255,255,255,0.1);'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg border-2 bg-dark-subtle text-light',
                'style': 'border-color: rgba(255,255,255,0.1);'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hanya tampilkan aset yang statusnya 'available' untuk dibooking
        self.fields['asset'].queryset = Asset.objects.filter(status='available')
        self.fields['asset'].empty_label = "Pilih alat yang ingin dibooking..."
