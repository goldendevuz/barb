from rest_framework import serializers
from .models import AutomationRule

class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = [
            "id",
            "name",
            "trigger",
            "conditions",
            "actions",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
