from rest_framework import views, status
from rest_framework.response import Response
from core.utils.http import IsAuthenticatedOrBot
from .selectors import get_dashboard_metrics
from .ai_recommender import predict_no_show_risk

class DashboardMetricsView(views.APIView):
    """
    API endpoint exposing analytical insights and stats for the SaaS dashboard.
    """
    permission_classes = [IsAuthenticatedOrBot]

    def get(self, request, *args, **kwargs):
        try:
            metrics = get_dashboard_metrics()
            return Response(metrics, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerNoShowRiskView(views.APIView):
    """
    API endpoint providing AI-based No-Show risk prediction for a specific customer.
    """
    permission_classes = [IsAuthenticatedOrBot]

    def get(self, request, customer_id, *args, **kwargs):
        try:
            prediction = predict_no_show_risk(customer_id)
            return Response(prediction, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GlobalAdminStatsView(views.APIView):
    """
    Superuser-level API endpoint exposing global system metrics across all tenants.
    """
    permission_classes = [IsAuthenticatedOrBot]

    def get(self, request, *args, **kwargs):
        # Allow superusers or bots
        if not request.user.is_superuser and request.META.get("HTTP_X_BOT_TOKEN") is None:
            return Response({"error": "Siz superuser emassiz!"}, status=status.HTTP_403_FORBIDDEN)
            
        from apps.staff.models import Barbershop, Staff
        from apps.customers.models import Customer
        from apps.appointments.models import Appointment
        from apps.payments.models import Payment
        from django.db.models import Sum

        total_branches = Barbershop.objects.count()
        total_barbers = Staff.objects.filter(role="barber").count()
        total_clients = Customer.objects.count()
        total_bookings = Appointment.objects.count()
        
        total_revenue = Payment.objects.filter(status="completed").aggregate(
            total=Sum("amount")
        )["total"] or 0.0

        return Response({
            "total_branches": total_branches,
            "total_barbers": total_barbers,
            "total_clients": total_clients,
            "total_bookings": total_bookings,
            "total_revenue": float(total_revenue),
        }, status=status.HTTP_200_OK)


