from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "type",
            "entity_type",
            "entity_id",
            "payload",
            "actor_type",
            "actor_id",
            "created_at",
        ]
        read_only_fields = fields
