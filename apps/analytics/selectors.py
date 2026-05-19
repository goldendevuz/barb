from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from apps.payments.models import Payment
from apps.services.models import Service
from apps.staff.models import Staff

def get_dashboard_metrics() -> dict:
    """
    Retrieves aggregated metrics for the real-time SaaS dashboard.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # 1. Financial metrics (completed payments)
    total_revenue = Payment.objects.filter(status="completed").aggregate(total=Sum("amount"))["total"] or 0.0
    
    # 2. Appointment metrics (Total)
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status="completed").count()
    cancelled_appointments = Appointment.objects.filter(status="cancelled").count()
    no_shows = Appointment.objects.filter(status="no_show").count()
    
    # Calculate no-show rate
    no_show_rate = 0.0
    if total_appointments > 0:
        no_show_rate = round((no_shows / total_appointments) * 100, 2)
        
    # 3. Today's appointments
    today_appointments = Appointment.objects.filter(start_time__range=(today_start, today_end))
    today_count = today_appointments.count()
    today_completed = today_appointments.filter(status="completed").count()
    today_active = today_appointments.filter(status__in=["created", "confirmed", "arrived", "in_service"]).count()
    
    # 4. Top Services
    top_services = (
        Service.objects.annotate(bookings_count=Count("appointments"))
        .filter(bookings_count__gt=0)
        .order_by("-bookings_count")[:5]
    )
    top_services_data = [
        {"id": s.id, "name": s.name, "bookings": s.bookings_count, "price": float(s.price)}
        for s in top_services
    ]
    
    # 5. Top Barbers (Staff)
    top_staff = (
        Staff.objects.annotate(bookings_count=Count("appointments"))
        .filter(bookings_count__gt=0)
        .order_by("-bookings_count")[:5]
    )
    top_staff_data = [
        {"id": st.id, "name": f"{st.first_name} {st.last_name}".strip(), "role": st.role, "bookings": st.bookings_count}
        for st in top_staff
    ]
    
    return {
        "revenue": {
            "total_earnings": float(total_revenue),
        },
        "appointments": {
            "total": total_appointments,
            "completed": completed_appointments,
            "cancelled": cancelled_appointments,
            "no_shows": no_shows,
            "no_show_rate_percent": no_show_rate,
        },
        "today": {
            "total": today_count,
            "completed": today_completed,
            "active": today_active,
        },
        "top_services": top_services_data,
        "top_staff": top_staff_data,
    }
