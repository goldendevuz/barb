import logging
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from apps.notifications.manager import send_notification
from .models import Appointment

logger = logging.getLogger(__name__)

@shared_task
def send_appointment_reminders_task():
    """
    Periodic task running every 30-60 minutes to send reminders
    for appointments starting in 1 to 2 hours.
    """
    now = timezone.now()
    reminder_window_start = now + timedelta(hours=1)
    reminder_window_end = now + timedelta(hours=2)
    
    # Fetch confirmed/created appointments in the next 1-2 hours
    upcoming_appointments = Appointment.objects.select_related("customer", "staff", "service").filter(
        status__in=["created", "confirmed"],
        start_time__range=(reminder_window_start, reminder_window_end)
    )
    
    sent_count = 0
    for appt in upcoming_appointments:
        customer = appt.customer
        staff = appt.staff
        service = appt.service
        
        # Format the start time for presentation
        time_str = appt.start_time.strftime("%H:%M (%d-%b)")
        message = (
            f"🔔 Loyihamiz eslatmasi!\n\n"
            f"Hurmatli {customer.first_name}, sizning {time_str} da "
            f"ustamiz {staff.first_name} ga <b>{service.name}</b> xizmati uchun "
            f"buyurtmangiz bor. Sizni kutib qolamiz!"
        )
        
        # Send notification
        send_notification(
            recipient_phone=customer.phone,
            message=message,
            telegram_id=customer.telegram_id
        )
        sent_count += 1
        
    logger.info(f"⏰ Reminder job processed: sent {sent_count} reminders for upcoming appointments.")
    return f"Sent {sent_count} reminders"
