from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Barber, Service, Client, Booking
from .serializers import BarberSerializer, ServiceSerializer, ClientSerializer, BookingSerializer

class BarberViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().select_related('client', 'barber', 'service')
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    today = timezone.now().date()
    
    today_bookings = Booking.objects.filter(date=today)
    today_income = today_bookings.filter(status=Booking.STATUS_DONE).aggregate(total=Sum('price'))['total'] or 0
    
    active_barbers = Barber.objects.filter(active=True).count()
    
    monthly_income = Booking.objects.filter(
        date__month=today.month, 
        date__year=today.year,
        status=Booking.STATUS_DONE
    ).aggregate(total=Sum('price'))['total'] or 0

    return Response({
        'today_bookings_count': today_bookings.count(),
        'today_income': today_income,
        'active_barbers': active_barbers,
        'monthly_income': monthly_income
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def top_statistics(request):
    top_services = Booking.objects.values('service__name').annotate(count=Count('id')).order_by('-count')[:5]
    top_barbers = Booking.objects.values('barber__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    return Response({
        'top_services': top_services,
        'top_barbers': top_barbers
    })
