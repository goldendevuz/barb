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

