from django.urls import re_path
from .consumers import LiveMetricsConsumer

websocket_urlpatterns = [
    re_path(r"ws/live-metrics/$", LiveMetricsConsumer.as_asgi()),
]
