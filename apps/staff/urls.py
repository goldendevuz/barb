from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, BarberSignupAPIView, BarberScheduleViewSet, BarbershopViewSet

router = DefaultRouter()
router.register(r"staff", StaffViewSet, basename="staff")
router.register(r"schedules", BarberScheduleViewSet, basename="schedule")
router.register(r"barbershops", BarbershopViewSet, basename="barbershop")


urlpatterns = [
    path("staff/signup/", BarberSignupAPIView.as_view(), name="barber-signup"),
    path("", include(router.urls)),
]

