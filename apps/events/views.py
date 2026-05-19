from rest_framework import viewsets, mixins
from core.utils.http import IsAuthenticatedOrBot
from .models import Event
from .serializers import EventSerializer

class EventViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only viewset for events to see event logs.
    """
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrBot]
    filterset_fields = ["type", "entity_type", "entity_id"]
