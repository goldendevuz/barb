import logging
from django.conf import settings
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class BotTokenAuthentication(BaseAuthentication):
    """
    Custom authentication to allow the Telegram bot to securely access backend APIs
    using a special secure header `X-Bot-Token`.
    """
    def authenticate(self, request):
        bot_token = request.headers.get("X-Bot-Token")
        if not bot_token:
            return None
        
        expected_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        if not expected_token:
            logger.warning("⚠️ Bot Token authentication attempted but TELEGRAM_BOT_TOKEN is not configured in settings.")
            return None
            
        if bot_token != expected_token:
            raise AuthenticationFailed("Invalid Bot Token")
            
        # Return a dummy bot user. We can fetch or create a service user if necessary.
        from django.contrib.auth import get_user_model
        User = get_user_model()
        bot_user, _ = User.objects.get_or_create(
            username="telegram_bot",
            email="bot@barber.crm",
            is_staff=True
        )
        return (bot_user, None)


class IsAuthenticatedOrBot(permissions.BasePermission):
    """
    Allows access to authenticated users or requests authenticated via Bot Token.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and (
                request.user.is_authenticated or 
                request.user.username == "telegram_bot"
            )
        )
