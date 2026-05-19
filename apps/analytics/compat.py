import logging
import pytz
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, viewsets, views, status
from rest_framework.response import Response
from core.utils.http import IsAuthenticatedOrBot

from apps.staff.models import Staff
from apps.customers.models import Customer
from apps.services.models import Service
from apps.appointments.models import Appointment
from apps.appointments.services import create_appointment, transition_appointment
from apps.payments.models import Payment

logger = logging.getLogger(__name__)

# ── 1. BARBER (STAFF) COMPATIBILITY ──────────────────────────────────────────

class BarberCompatSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    active = serializers.BooleanField(source="is_active", required=False)

    class Meta:
        model = Staff
        fields = ["id", "name", "phone", "active"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def create(self, validated_data):
        request = self.context["request"]
        name = request.data.get("name", "")
        parts = name.split(" ", 1)
        validated_data["first_name"] = parts[0]
        validated_data["last_name"] = parts[1] if len(parts) > 1 else ""
        validated_data["role"] = "barber"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        name = request.data.get("name", "")
        if name:
            parts = name.split(" ", 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ""
        return super().update(instance, validated_data)


class BarberCompatViewSet(viewsets.ModelViewSet):
    serializer_class = BarberCompatSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return Staff.objects.filter(role="barber").order_by("first_name")
        try:
            staff_profile = user.staff_profile
            if staff_profile.role == "barber":
                return Staff.objects.filter(id=staff_profile.id)
            elif staff_profile.role == "admin":
                return Staff.objects.filter(role="barber", barbershop=staff_profile.barbershop).order_by("first_name")
        except Exception:
            pass
        if user.is_superuser:
            return Staff.objects.filter(role="barber").order_by("first_name")
        return Staff.objects.none()


# ── 2. CLIENT (CUSTOMER) COMPATIBILITY ────────────────────────────────────────

class ClientCompatSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ["id", "telegram_id", "name", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def create(self, validated_data):
        request = self.context["request"]
        name = request.data.get("name", "")
        parts = name.split(" ", 1)
        validated_data["first_name"] = parts[0]
        validated_data["last_name"] = parts[1] if len(parts) > 1 else ""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        name = request.data.get("name", "")
        if name:
            parts = name.split(" ", 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ""
        return super().update(instance, validated_data)


class ClientCompatViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = ClientCompatSerializer
    permission_classes = [IsAuthenticatedOrBot]


# ── 3. BOOKING (APPOINTMENT) COMPATIBILITY ────────────────────────────────────

class BookingCompatSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source="customer")
    barber = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all(), source="staff")
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    
    client_name = serializers.SerializerMethodField()
    barber_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "client", "client_name", "barber", "barber_name", 
            "service", "service_name", "date", "time", "price", "status"
        ]

    def get_client_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip()

    def get_barber_name(self, obj):
        return f"{obj.staff.first_name} {obj.staff.last_name}".strip()

    def get_service_name(self, obj):
        return obj.service.name

    def get_date(self, obj):
        return obj.start_time.strftime("%Y-%m-%d")

    def get_time(self, obj):
        return obj.start_time.strftime("%H:%M:%S")

    def get_price(self, obj):
        return float(obj.service.price)

    def get_status(self, obj):
        mapping = {
            "created": "pending",
            "confirmed": "confirmed",
            "cancelled": "cancelled",
            "completed": "done",
            "arrived": "confirmed",
            "in_service": "confirmed",
            "no_show": "cancelled",
        }
        return mapping.get(obj.status, "pending")


class BookingCompatViewSet(viewsets.ModelViewSet):
    serializer_class = BookingCompatSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return Appointment.objects.all().order_by("-start_time")
        try:
            staff_profile = user.staff_profile
            if staff_profile.role == "barber":
                return Appointment.objects.filter(staff=staff_profile).order_by("-start_time")
            elif staff_profile.role == "admin":
                return Appointment.objects.filter(staff__barbershop=staff_profile.barbershop).order_by("-start_time")
        except Exception:
            pass
        if user.is_superuser:
            return Appointment.objects.all().order_by("-start_time")
        return Appointment.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        date_str = request.data.get("date")
        time_str = request.data.get("time")
        if not date_str or not time_str:
            return Response({"error": "date and time are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if len(time_str.split(":")) == 2:
                time_str += ":00"
            start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            local_tz = pytz.timezone(settings.TIME_ZONE)
            start_time = local_tz.localize(start_time)
        except Exception as e:
            return Response({"error": f"Invalid date/time format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        status_input = request.data.get("status", "pending")
        status_mapping = {
            "pending": "created",
            "confirmed": "confirmed",
            "cancelled": "cancelled",
            "done": "completed",
        }
        status_val = status_mapping.get(status_input, "created")

        actor_id = request.user.id if request.user else None
        actor_type = "staff"

        try:
            appt = create_appointment(
                customer_id=data["customer"].id,
                staff_id=data["staff"].id,
                service_id=data["service"].id,
                start_time=start_time,
                actor_type=actor_type,
                actor_id=actor_id
            )
            
            if status_val != "created":
                appt = transition_appointment(
                    appointment_id=appt.id,
                    new_status=status_val,
                    actor_type=actor_type,
                    actor_id=actor_id
                )
                
            response_serializer = self.get_serializer(appt)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        new_status_input = request.data.get("status")
        if new_status_input:
            status_mapping = {
                "pending": "created",
                "confirmed": "confirmed",
                "cancelled": "cancelled",
                "done": "completed",
            }
            target_status = status_mapping.get(new_status_input)
            if target_status and target_status != instance.status:
                try:
                    transition_appointment(
                        appointment_id=instance.id,
                        new_status=target_status,
                        actor_type="staff",
                        actor_id=request.user.id if request.user else None
                    )
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    
        return super().update(request, *args, **kwargs)


# ── 4. DASHBOARD COMPATIBILITY VIEW ──────────────────────────────────────────

class DashboardStatsView(views.APIView):
    permission_classes = [IsAuthenticatedOrBot]

    def get(self, request, *args, **kwargs):
        from django.db.models import Sum
        
        user = request.user
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timezone.timedelta(days=1)
        
        # Get tenant filters
        barber_filter = None
        barbershop_filter = None
        
        if user and not user.is_anonymous:
            try:
                staff_profile = user.staff_profile
                if staff_profile.role == "barber":
                    barber_filter = staff_profile
                elif staff_profile.role == "admin":
                    barbershop_filter = staff_profile.barbershop
            except Exception:
                pass

        # 1. Today's booking count
        q_appt = Appointment.objects.filter(start_time__range=(today_start, today_end))
        if barber_filter:
            q_appt = q_appt.filter(staff=barber_filter)
        elif barbershop_filter:
            q_appt = q_appt.filter(staff__barbershop=barbershop_filter)
        today_count = q_appt.count()
        
        # 2. Today's completed payments
        q_pay = Payment.objects.filter(status="completed", created_at__range=(today_start, today_end))
        if barber_filter:
            q_pay = q_pay.filter(appointment__staff=barber_filter)
        elif barbershop_filter:
            q_pay = q_pay.filter(appointment__staff__barbershop=barbershop_filter)
        today_income = q_pay.aggregate(total=Sum("amount"))["total"] or 0.0
        
        # 3. Monthly completed payments
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        q_pay_month = Payment.objects.filter(status="completed", created_at__gte=month_start)
        if barber_filter:
            q_pay_month = q_pay_month.filter(appointment__staff=barber_filter)
        elif barbershop_filter:
            q_pay_month = q_pay_month.filter(appointment__staff__barbershop=barbershop_filter)
        monthly_income = q_pay_month.aggregate(total=Sum("amount"))["total"] or 0.0
        
        # 4. Active barbers count
        q_barbers = Staff.objects.filter(role="barber", is_active=True)
        if barbershop_filter:
            q_barbers = q_barbers.filter(barbershop=barbershop_filter)
        elif barber_filter:
            q_barbers = q_barbers.filter(id=barber_filter.id)
        active_barbers = q_barbers.count()
        
        return Response({
            "today_bookings_count": today_count,
            "today_income": float(today_income),
            "monthly_income": float(monthly_income),
            "active_barbers": active_barbers,
        })

