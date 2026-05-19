from typing import Any, Dict, Optional
from core.domain.events import emit_event
from apps.appointments.models import Appointment
from .models import Payment

def create_payment(
    appointment_id: int,
    amount: float,
    method: str = "cash",
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Payment:
    """
    Creates a new payment in pending status.
    """
    appointment = Appointment.objects.get(id=appointment_id)
    payment = Payment.objects.create(
        appointment=appointment,
        amount=amount,
        method=method,
        status="pending"
    )
    return payment


def complete_payment(
    payment_id: int,
    transaction_id: Optional[str] = None,
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Payment:
    """
    Completes a payment and emits a payment_received event.
    """
    payment = Payment.objects.select_related("appointment", "appointment__customer").get(id=payment_id)
    payment.status = "completed"
    if transaction_id:
        payment.transaction_id = transaction_id
    payment.save()
    
    # Emit event
    payload = {
        "payment_id": payment.id,
        "appointment_id": payment.appointment.id,
        "customer_id": payment.appointment.customer.id,
        "customer_name": f"{payment.appointment.customer.first_name} {payment.appointment.customer.last_name}".strip(),
        "amount": float(payment.amount),
        "method": payment.method,
        "status": payment.status,
        "transaction_id": payment.transaction_id
    }
    
    emit_event(
        event_type="payment_received",
        entity_type="payment",
        entity_id=payment.id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id
    )
    
    return payment
