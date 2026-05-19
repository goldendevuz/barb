from django.urls import path
from .views import DashboardMetricsView, CustomerNoShowRiskView, GlobalAdminStatsView

urlpatterns = [
    path("analytics/dashboard/", DashboardMetricsView.as_view(), name="dashboard-metrics"),
    path("analytics/no-show-risk/<int:customer_id>/", CustomerNoShowRiskView.as_view(), name="customer-no-show-risk"),
    path("admin/global-stats/", GlobalAdminStatsView.as_view(), name="global-admin-stats"),
]

