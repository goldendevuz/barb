from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.utils.http import IsAuthenticatedOrBot
from .models import Customer
from .serializers import CustomerSerializer
from .services import create_customer, update_customer_telegram

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        data = serializer.validated_data
        
        # Determine actor
        actor_type = "staff"
        actor_id = request.user.id if request.user else None
        if request.user and request.user.username == "telegram_bot":
            actor_type = "bot"
            
        # Create through service
        customer = create_customer(
            first_name=data.get("first_name"),
            phone=data.get("phone"),
            last_name=data.get("last_name", ""),
            telegram_id=data.get("telegram_id"),
            actor_type=actor_type,
            actor_id=actor_id
        )
        
        response_serializer = self.get_serializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="by-phone")
    def get_or_create_by_phone(self, request):
        """
        Special API endpoint used by the Telegram bot to fetch or create a customer by phone number.
        """
        phone = request.data.get("phone")
        first_name = request.data.get("first_name", "Bot Customer")
        telegram_id = request.data.get("telegram_id")
        
        if not phone:
            return Response({"error": "Phone is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            if telegram_id and customer.telegram_id != telegram_id:
                customer = update_customer_telegram(
                    customer_id=customer.id,
                    telegram_id=telegram_id,
                    actor_type="bot"
                )
        else:
            customer = create_customer(
                first_name=first_name,
                phone=phone,
                telegram_id=telegram_id,
                actor_type="bot"
            )
            
        serializer = self.get_serializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
