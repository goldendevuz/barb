from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('barbers', views.BarberViewSet)
router.register('services', views.ServiceViewSet)
router.register('clients', views.ClientViewSet)
router.register('bookings', views.BookingViewSet)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('top-stats/', views.top_statistics, name='top_stats'),
    path('', include(router.urls)),
]
