from rest_framework import serializers
from apps.customers.serializers import CustomerSerializer
from apps.staff.serializers import StaffSerializer
from apps.services.serializers import ServiceSerializer
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source="customer", read_only=True)
    staff_detail = StaffSerializer(source="staff", read_only=True)
    service_detail = ServiceSerializer(source="service", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer",
            "customer_detail",
            "staff",
            "staff_detail",
            "service",
            "service_detail",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "end_time", "created_at", "updated_at"]
