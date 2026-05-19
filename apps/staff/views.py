from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from core.utils.http import IsAuthenticatedOrBot
from .models import Staff, BarberSchedule, Barbershop
from .serializers import StaffSerializer, BarberSignupSerializer, BarberScheduleSerializer, BarbershopSerializer

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            # For bots or anonymous requests with bot token headers
            return Staff.objects.all().order_by("first_name")
            
        try:
            staff_profile = user.staff_profile
            # A barber only sees their own profile or their branch members
            if staff_profile.role == "barber":
                return Staff.objects.filter(id=staff_profile.id)
            elif staff_profile.role == "admin":
                return Staff.objects.filter(barbershop=staff_profile.barbershop)
        except Exception:
            pass
            
        if user.is_superuser:
            return Staff.objects.all().order_by("first_name")
            
        return Staff.objects.none()


class BarberSignupAPIView(views.APIView):
    """
    API endpoint allowing new barbers to sign up for CRM accounts dynamically.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = BarberSignupSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response({
                "message": "Sartarosh muvaffaqiyatli ro'yxatdan o'tdi!",
                "barber_id": staff.id,
                "barbershop": staff.barbershop.name if staff.barbershop else None
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarbershopViewSet(viewsets.ModelViewSet):
    queryset = Barbershop.objects.all()
    serializer_class = BarbershopSerializer
    permission_classes = [permissions.AllowAny]


class BarberScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = BarberScheduleSerializer
    permission_classes = [IsAuthenticatedOrBot]


    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return BarberSchedule.objects.all()
            
        try:
            staff_profile = user.staff_profile
            # Barbers manage their own schedule
            if staff_profile.role == "barber":
                return BarberSchedule.objects.filter(staff=staff_profile)
            elif staff_profile.role == "admin":
                # Admin manages all schedules in the branch
                return BarberSchedule.objects.filter(staff__barbershop=staff_profile.barbershop)
        except Exception:
            pass
            
        if user.is_superuser:
            return BarberSchedule.objects.all()
            
        return BarberSchedule.objects.none()

