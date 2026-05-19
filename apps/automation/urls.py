from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AutomationRuleViewSet

router = DefaultRouter()
router.register(r"automation", AutomationRuleViewSet, basename="automation")

urlpatterns = [
    path("", include(router.urls)),
]
