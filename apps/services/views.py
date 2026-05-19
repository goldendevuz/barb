from rest_framework import viewsets
from core.utils.http import IsAuthenticatedOrBot
from .models import Service
from .serializers import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("name")
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrBot]
