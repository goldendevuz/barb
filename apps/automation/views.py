from rest_framework import viewsets
from core.utils.http import IsAuthenticatedOrBot
from .models import AutomationRule
from .serializers import AutomationRuleSerializer

class AutomationRuleViewSet(viewsets.ModelViewSet):
    queryset = AutomationRule.objects.all().order_by("-created_at")
    serializer_class = AutomationRuleSerializer
    permission_classes = [IsAuthenticatedOrBot]
