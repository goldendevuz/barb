from typing import Any, Dict, Optional
from core.domain.events import emit_event
from .models import Customer

def create_customer(
    first_name: str,
    phone: str,
    last_name: str = "",
    telegram_id: Optional[str] = None,
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Customer:
    """
    Creates a new customer and emits a customer_created event.
    """
    customer = Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        telegram_id=telegram_id
    )
    
    payload = {
        "customer_id": customer.id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "telegram_id": customer.telegram_id,
        "status": customer.status
    }
    
    emit_event(
        event_type="customer_created",
        entity_type="customer",
        entity_id=customer.id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id
    )
    
    return customer


def update_customer_telegram(
    customer_id: int,
    telegram_id: str,
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Customer:
    """
    Updates a customer's telegram_id and emits a customer_updated event.
    """
    customer = Customer.objects.get(id=customer_id)
    customer.telegram_id = telegram_id
    customer.save()
    
    payload = {
        "customer_id": customer.id,
        "telegram_id": customer.telegram_id,
        "phone": customer.phone
    }
    
    emit_event(
        event_type="customer_telegram_linked",
        entity_type="customer",
        entity_id=customer.id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id
    )
    
    return customer
