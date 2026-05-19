import logging
from typing import Optional
from .models import NotificationLog

logger = logging.getLogger(__name__)

def send_notification(
    recipient_phone: str,
    message: str,
    telegram_id: Optional[str] = None
) -> NotificationLog:
    """
    Core function to abstract and route notifications.
    Prefers Telegram if a telegram_id is provided, otherwise falls back to SMS.
    """
    from .tasks import send_notification_async_task
    
    if telegram_id:
        channel = "telegram"
        recipient = telegram_id
    else:
        channel = "sms"
        recipient = recipient_phone
        
    # 1. Log the notification as pending
    log = NotificationLog.objects.create(
        recipient=recipient,
        channel=channel,
        message=message,
        status="pending"
    )
    
    # 2. Queue asynchronous delivery
    send_notification_async_task.delay(log.id)
    logger.info(f"📬 Queued notification #{log.id} to {recipient} via {channel}")
    
    return log
