from rest_framework import viewsets
from core.utils.http import IsAuthenticatedOrBot
from .models import Staff
from .serializers import StaffSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().order_by("first_name")
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticatedOrBot]
