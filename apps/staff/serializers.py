from rest_framework import serializers
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "role",
            "telegram_id",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
