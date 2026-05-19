import logging
import requests
from django.conf import settings
from celery import shared_task
from .models import NotificationLog

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_async_task(self, log_id: int):
    """
    Celery task to send a notification (SMS or Telegram) asynchronously.
    """
    try:
        log = NotificationLog.objects.get(id=log_id)
    except NotificationLog.DoesNotExist:
        logger.error(f"NotificationLog #{log_id} not found.")
        return
        
    logger.info(f"🚀 Sending notification #{log.id} via {log.channel}")
    
    if log.channel == "telegram":
        success, error = _send_telegram_api(log.recipient, log.message)
    elif log.channel == "sms":
        success, error = _send_sms_api(log.recipient, log.message)
    else:
        success, error = False, "Unsupported notification channel"
        
    if success:
        log.status = "sent"
        log.error_message = None
        logger.info(f"✅ Notification #{log.id} sent successfully")
    else:
        log.status = "failed"
        log.error_message = error
        logger.error(f"❌ Notification #{log.id} failed: {error}")
        # Retry for temporary errors
        try:
            self.retry()
        except self.MaxRetriesExceededError:
            logger.error(f"❌ Max retries exceeded for notification #{log.id}")
            
    log.save()


def _send_telegram_api(chat_id: str, message: str) -> (bool, str):
    """
    Sends message directly via Telegram Bot API using requests.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    if not token:
        return False, "TELEGRAM_BOT_TOKEN settings is empty"
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            return True, ""
        else:
            err_desc = res_data.get("description", "Unknown Telegram error")
            return False, f"Telegram API error: {err_desc}"
    except Exception as e:
        return False, f"HTTP request failed: {str(e)}"


def _send_sms_api(phone: str, message: str) -> (bool, str):
    """
    Simulates SMS dispatching. Can be integrated with Eskiz or other SMS provider.
    """
    sms_url = getattr(settings, "SMS_URL", None)
    sms_token = getattr(settings, "SMS_TOKEN", None)
    
    # Simulating/Logging for development if not configured
    if not sms_url or not sms_token:
        logger.info(f"📝 [SMS Simulator] To: {phone} | Message: {message}")
        return True, ""
        
    # Example production post:
    try:
        headers = {"Authorization": f"Bearer {sms_token}"}
        payload = {"mobile_phone": phone, "message": message}
        response = requests.post(sms_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, ""
        return False, f"SMS Provider HTTP {response.status_code}"
    except Exception as e:
        return False, f"SMS Provider connection error: {str(e)}"
