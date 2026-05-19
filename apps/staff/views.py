from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import hmac
import hashlib
import logging
from decouple import config

logger = logging.getLogger(__name__)

from core.utils.http import IsAuthenticatedOrBot
from .models import Staff, BarberSchedule, Barbershop
from .serializers import StaffSerializer, BarberSignupSerializer, BarberScheduleSerializer, BarbershopSerializer

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticatedOrBot]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            # For bots or anonymous requests with bot token headers
            return Staff.objects.all().order_by("first_name")
            
        try:
            staff_profile = user.staff_profile
            # A barber only sees their own profile or their branch members
            if staff_profile.role == "barber":
                return Staff.objects.filter(id=staff_profile.id)
            elif staff_profile.role == "admin":
                return Staff.objects.filter(barbershop=staff_profile.barbershop)
        except Exception:
            pass
            
        if user.is_superuser:
            return Staff.objects.all().order_by("first_name")
            
        return Staff.objects.none()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SocialAuthAPIView(views.APIView):
    """
    Unified API endpoint for Social Authentication (Google OAuth & Telegram Widget).
    Returns JWT tokens on successful authentication.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        provider = request.data.get("provider")
        if not provider:
            return Response({"error": "provider is required"}, status=status.HTTP_400_BAD_REQUEST)

        if provider == "telegram":
            telegram_data = request.data.get("auth_data", {})
            bot_token = config("TELEGRAM_BOT_TOKEN", default="")
            
            received_hash = telegram_data.get("hash")
            if not received_hash or not bot_token:
                return Response({"error": "Invalid auth_data or bot_token"}, status=status.HTTP_400_BAD_REQUEST)
                
            auth_fields = {k: v for k, v in telegram_data.items() if k != "hash"}
            sorted_fields = sorted([f"{k}={v}" for k, v in auth_fields.items()])
            check_string = "\n".join(sorted_fields)
            
            secret_key = hashlib.sha256(bot_token.encode()).digest()
            calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(calculated_hash, received_hash):
                return Response({"error": "Telegram data hash verification failed"}, status=status.HTTP_401_UNAUTHORIZED)
                
            username = f"telegram_{telegram_data.get('id')}"
            first_name = telegram_data.get("first_name", "")
            last_name = telegram_data.get("last_name", "")
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name
                }
            )
            
            if not hasattr(user, 'staff_profile'):
                barbershop, _ = Barbershop.objects.get_or_create(
                    name="Asosiy Sartaroshxona",
                    defaults={"address": "Toshkent shahri"}
                )
                Staff.objects.get_or_create(
                    user=user,
                    defaults={
                        "barbershop": barbershop,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "barber",
                        "telegram_id": telegram_data.get("id"),
                        "phone": f"+0000_{telegram_data.get('id')}"
                    }
                )

            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Telegram orqali muvaffaqiyatli kirildi!",
                "tokens": tokens,
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "is_superuser": user.is_superuser
                }
            }, status=status.HTTP_200_OK)

        elif provider == "google":
            email = request.data.get("email")
            first_name = request.data.get("first_name", "")
            last_name = request.data.get("last_name", "")
            token = request.data.get("token")
            
            if not email or not token:
                return Response({"error": "email and token are required"}, status=status.HTTP_400_BAD_REQUEST)
                
            username = email.split("@")[0]
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )
            
            if not hasattr(user, 'staff_profile'):
                barbershop, _ = Barbershop.objects.get_or_create(
                    name="Asosiy Sartaroshxona",
                    defaults={"address": "Toshkent shahri"}
                )
                Staff.objects.get_or_create(
                    user=user,
                    defaults={
                        "barbershop": barbershop,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "barber",
                        "phone": f"+1111_{hash(email) % 1000000}"
                    }
                )

            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Google orqali muvaffaqiyatli kirildi!",
                "tokens": tokens,
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "is_superuser": user.is_superuser
                }
            }, status=status.HTTP_200_OK)

        return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)


class BarberSignupAPIView(views.APIView):
    """
    API endpoint allowing new barbers to sign up for CRM accounts dynamically.
    """
    permission_classes = [permissions.AllowAny]


    def post(self, request, *args, **kwargs):
        serializer = BarberSignupSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response({
                "message": "Sartarosh muvaffaqiyatli ro'yxatdan o'tdi!",
                "barber_id": staff.id,
                "barbershop": staff.barbershop.name if staff.barbershop else None
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BarbershopViewSet(viewsets.ModelViewSet):
    queryset = Barbershop.objects.all()
    serializer_class = BarbershopSerializer
    permission_classes = [permissions.AllowAny]


class BarberScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = BarberScheduleSerializer
    permission_classes = [IsAuthenticatedOrBot]


    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return BarberSchedule.objects.all()
            
        try:
            staff_profile = user.staff_profile
            # Barbers manage their own schedule
            if staff_profile.role == "barber":
                return BarberSchedule.objects.filter(staff=staff_profile)
            elif staff_profile.role == "admin":
                # Admin manages all schedules in the branch
                return BarberSchedule.objects.filter(staff__barbershop=staff_profile.barbershop)
        except Exception:
            pass
            
        if user.is_superuser:
            return BarberSchedule.objects.all()
            
        return BarberSchedule.objects.none()


class BarberTelegramLinkAPIView(views.APIView):
    """
    Endpoint for barbers to generate a secure verification link
    to hook their Telegram accounts and receive automated booking alerts.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Let bots access

    def get(self, request, *args, **kwargs):
        try:
            staff = request.user.staff_profile
        except Exception:
            return Response({"error": "Sartarosh profili topilmadi!"}, status=status.HTTP_404_NOT_FOUND)

        from django.conf import settings
        import hashlib

        raw_str = f"{staff.id}_{settings.SECRET_KEY}"
        token = hashlib.md5(raw_str.encode()).hexdigest()[:10]
        
        bot_username = config("TELEGRAM_BOT_USERNAME", default="sharb_bot")
        link = f"https://t.me/{bot_username}?start=staff_{staff.id}_{token}"

        return Response({
            "is_linked": bool(staff.telegram_id),
            "telegram_id": staff.telegram_id,
            "link": link,
            "start_param": f"staff_{staff.id}_{token}"
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Bot token validation
        if request.META.get("HTTP_X_BOT_TOKEN") is None and not request.user.is_superuser:
            return Response({"error": "Faqat bot bu amaliyotni bajara oladi!"}, status=status.HTTP_403_FORBIDDEN)
            
        staff_id = request.data.get("staff_id")
        token = request.data.get("token")
        telegram_id = request.data.get("telegram_id")
        
        if not staff_id or not token or not telegram_id:
            return Response({"error": "Barcha parametrlar majburiy!"}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.conf import settings
        import hashlib
        from apps.staff.models import Staff
        
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({"error": "Sartarosh topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
            
        # Verify token
        raw_str = f"{staff.id}_{settings.SECRET_KEY}"
        expected_token = hashlib.md5(raw_str.encode()).hexdigest()[:10]
        
        if token != expected_token:
            return Response({"error": "Xavfsizlik kaliti noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)
            
        staff.telegram_id = str(telegram_id)
        staff.save()
        
        return Response({
            "success": True,
            "staff_name": f"{staff.first_name} {staff.last_name}".strip()
        }, status=status.HTTP_200_OK)



