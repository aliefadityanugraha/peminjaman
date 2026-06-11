from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from .models import Reservation
from .serializers import ReservationSerializer, ReservationReviewSerializer
from .permissions import IsAdminUserRole

class PendingReservationsAPIView(APIView):
    """
    API View khusus Admin untuk mendapatkan daftar pemesanan/reservasi
    yang saat ini berstatus 'pending'.
    
    Akses dibatasi hanya untuk User terautentikasi dengan role 'admin'.
    """
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request, *args, **kwargs):
        # Ambil semua reservasi dengan status pending
        reservations = Reservation.objects.filter(status='pending').select_related('user', 'asset')
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewReservationAPIView(APIView):
    """
    API View khusus Admin untuk melakukan Approve atau Reject pada reservasi.
    Menerima metode PATCH atau PUT untuk memperbarui field 'status' dan 'admin_note'.
    
    Akses dibatasi hanya untuk User terautentikasi dengan role 'admin'.
    """
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get_object(self, pk):
        return get_object_or_404(Reservation, pk=pk)

    def put(self, request, pk, *args, **kwargs):
        """
        Mengubah status booking secara utuh (Approve/Reject dengan admin_note).
        """
        reservation = self.get_object(pk)
        serializer = ReservationReviewSerializer(reservation, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            # Kembalikan data lengkap reservasi setelah diubah
            full_serializer = ReservationSerializer(reservation)
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        """
        Mengubah status booking secara parsial (Approve/Reject dengan admin_note).
        """
        reservation = self.get_object(pk)
        serializer = ReservationReviewSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Kembalikan data lengkap reservasi setelah diubah
            full_serializer = ReservationSerializer(reservation)
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
