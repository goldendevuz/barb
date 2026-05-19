import logging
from apps.appointments.models import Appointment
from apps.customers.models import Customer

logger = logging.getLogger(__name__)

def predict_no_show_risk(customer_id: int) -> dict:
    """
    AI Heuristic Classification Engine.
    Analyzes historical client metrics (total bookings, cancellations, no-show ratio)
    to dynamically evaluate and predict the probability of a No-Show.
    """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return {"risk_score": 0.0, "risk_level": "low", "recommendation": "Mijoz topilmadi"}

    # Fetch historical stats for the customer
    total_appointments = Appointment.objects.filter(customer_id=customer_id).count()
    if total_appointments == 0:
        # Cold start: new clients default to a baseline low-risk profile
        return {
            "risk_score": 15.0,
            "risk_level": "low",
            "recommendation": "Yangi mijoz. Standart xabarnoma yuborish tavsiya etiladi."
        }

    no_shows = Appointment.objects.filter(customer_id=customer_id, status="no_show").count()
    cancelled = Appointment.objects.filter(customer_id=customer_id, status="cancelled").count()
    completed = Appointment.objects.filter(customer_id=customer_id, status="completed").count()

    # Heuristic Weights (Feature engineering)
    # - Prior no-shows carry a heavy penalty (weight: 50)
    # - Cancellations carry a moderate penalty (weight: 20)
    # - Completed bookings reward loyalty (weight: -10)
    
    base_score = 20.0  # baseline probability
    
    no_show_rate = no_shows / total_appointments
    cancel_rate = cancelled / total_appointments
    completion_rate = completed / total_appointments
    
    risk_score = base_score + (no_show_rate * 60) + (cancel_rate * 25) - (completion_rate * 15)
    
    # Clip risk score between 5% and 95%
    risk_score = max(5.0, min(95.0, round(risk_score, 2)))
    
    if risk_score > 65.0:
        level = "high"
        rec = "⚠️ Yuqori xavf! Bandlik boshlanishidan 2 soat oldin majburiy telefon qo'ng'irog'i orqali tasdiqlash tavsiya etiladi."
    elif risk_score > 35.0:
        level = "medium"
        rec = "🔔 O'rtacha xavf. Telegram orqali qo'shimcha tasdiqlash xabarnomasi yuborish tavsiya etiladi."
    else:
        level = "low"
        rec = "✅ Ishonchli mijoz. Standart avtomatlashtirilgan eslatma yetarli."
        
    return {
        "risk_score": risk_score,
        "risk_level": level,
        "recommendation": rec,
        "features": {
            "total_bookings": total_appointments,
            "no_show_rate_percent": round(no_show_rate * 100, 1),
            "cancel_rate_percent": round(cancel_rate * 100, 1)
        }
    }
