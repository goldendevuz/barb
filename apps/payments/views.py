from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.utils.http import IsAuthenticatedOrBot
from .models import Payment
from .serializers import PaymentSerializer
from .services import create_payment, complete_payment

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by("-created_at")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        actor_type = "staff"
        actor_id = request.user.id if request.user else None
        if request.user and request.user.username == "telegram_bot":
            actor_type = "bot"

        payment = create_payment(
            appointment_id=data.get("appointment").id,
            amount=data.get("amount"),
            method=data.get("method", "cash"),
            actor_type=actor_type,
            actor_id=actor_id
        )
        
        response_serializer = self.get_serializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        transaction_id = request.data.get("transaction_id")
        
        actor_type = "staff"
        actor_id = request.user.id if request.user else None
        if request.user and request.user.username == "telegram_bot":
            actor_type = "bot"

        try:
            payment = complete_payment(
                payment_id=pk,
                transaction_id=transaction_id,
                actor_type=actor_type,
                actor_id=actor_id
            )
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
