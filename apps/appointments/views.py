from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.errors.base import StateTransitionError
from core.utils.http import IsAuthenticatedOrBot
from .models import Appointment
from .serializers import AppointmentSerializer
from .services import create_appointment, transition_appointment

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("-start_time")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        actor_type = "staff"
        actor_id = request.user.id if request.user else None
        if request.user and request.user.username == "telegram_bot":
            actor_type = "bot"

        try:
            appointment = create_appointment(
                customer_id=data.get("customer").id,
                staff_id=data.get("staff").id,
                service_id=data.get("service").id,
                start_time=data.get("start_time"),
                actor_type=actor_type,
                actor_id=actor_id
            )
            response_serializer = self.get_serializer(appointment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        """
        Transition an appointment's state. Expects `new_status` in body.
        """
        new_status = request.data.get("new_status")
        if not new_status:
            return Response({"error": "new_status is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        actor_type = "staff"
        actor_id = request.user.id if request.user else None
        if request.user and request.user.username == "telegram_bot":
            actor_type = "bot"

        try:
            appointment = transition_appointment(
                appointment_id=pk,
                new_status=new_status,
                actor_type=actor_type,
                actor_id=actor_id
            )
            serializer = self.get_serializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StateTransitionError as e:
            return Response({"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="by-telegram/(?P<telegram_id>[^/.]+)")
    def get_by_telegram(self, request, telegram_id=None):
        """
        Special API endpoint used by the Telegram bot to fetch upcoming bookings for a customer.
        """
        appointments = Appointment.objects.filter(
            customer__telegram_id=telegram_id,
            status__in=["created", "confirmed"]
        ).order_by("start_time")
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
