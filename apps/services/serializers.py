from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(source="is_active", required=False)
    duration = serializers.IntegerField(source="duration_minutes", required=False)

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "price",
            "duration_minutes",
            "is_active",
            "active",
            "duration",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

