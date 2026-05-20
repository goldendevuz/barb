from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.analytics.compat import (
    BarberCompatViewSet,
    ClientCompatViewSet,
    BookingCompatViewSet,
    DashboardStatsView,
)

def health_check(request):
    try:
        db_conn = connections["default"]
        db_conn.cursor()
    except OperationalError:
        return JsonResponse({"status": "unhealthy", "database": "unavailable"}, status=500)
    return JsonResponse({"status": "healthy", "database": "available"})

# Compatibility router for existing React frontend pages
compat_router = DefaultRouter()
compat_router.register(r"barbers", BarberCompatViewSet, basename="barber-compat")
compat_router.register(r"clients", ClientCompatViewSet, basename="client-compat")
compat_router.register(r"bookings", BookingCompatViewSet, basename="booking-compat")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ── Compatibility API Endpoints ──────────────────────────────────────────
    path("api/", include(compat_router.urls)),
    path("api/dashboard-stats/", DashboardStatsView.as_view(), name="dashboard-stats-compat"),
    
    # ── Standard App API Layers ──────────────────────────────────────────────
    path("api/", include("apps.customers.urls")),
    path("api/", include("apps.appointments.urls")),
    path("api/", include("apps.staff.urls")),
    path("api/", include("apps.services.urls")),
    path("api/", include("apps.payments.urls")),
    path("api/", include("apps.events.urls")),
    path("api/", include("apps.automation.urls")),
    path("api/", include("apps.analytics.urls")),
]

