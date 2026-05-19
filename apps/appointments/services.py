import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from django.utils import timezone
from core.errors.base import StateTransitionError
from core.domain.events import emit_event
from apps.customers.models import Customer
from apps.staff.models import Staff
from apps.services.models import Service
from .models import Appointment

logger = logging.getLogger(__name__)

# State Transitions Map: Defines valid next states from a current state
VALID_TRANSITIONS = {
    "created": ["confirmed", "cancelled"],
    "confirmed": ["arrived", "no_show", "cancelled"],
    "arrived": ["in_service", "cancelled"],
    "in_service": ["completed", "cancelled"],
    "completed": [],
    "cancelled": [],
    "no_show": [],
}

def create_appointment(
    customer_id: int,
    staff_id: int,
    service_id: int,
    start_time: datetime,
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Appointment:
    """
    Creates an appointment, calculates the end time based on service duration, and emits an event.
    """
    customer = Customer.objects.get(id=customer_id)
    staff = Staff.objects.get(id=staff_id)
    service = Service.objects.get(id=service_id)
    
    # Calculate end time
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    
    appointment = Appointment.objects.create(
        customer=customer,
        staff=staff,
        service=service,
        start_time=start_time,
        end_time=end_time,
        status="created"
    )
    
    # Emit event
    payload = {
        "appointment_id": appointment.id,
        "customer_id": customer.id,
        "customer_name": f"{customer.first_name} {customer.last_name}".strip(),
        "customer_phone": customer.phone,
        "staff_id": staff.id,
        "staff_name": f"{staff.first_name} {staff.last_name}".strip(),
        "service_name": service.name,
        "price": float(service.price),
        "start_time": appointment.start_time.isoformat(),
        "status": appointment.status
    }
    
    emit_event(
        event_type="appointment_created",
        entity_type="appointment",
        entity_id=appointment.id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id
    )
    
    return appointment


def transition_appointment(
    appointment_id: int,
    new_status: str,
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Appointment:
    """
    Transitions an appointment status according to state machine rules.
    Emits status changed and state specific events.
    """
    appointment = Appointment.objects.select_related("customer", "staff", "service").get(id=appointment_id)
    old_status = appointment.status
    
    # 1. State Machine check
    if new_status not in VALID_TRANSITIONS.get(old_status, []):
        raise StateTransitionError(
            f"Cannot transition appointment from state '{old_status}' to '{new_status}'"
        )
        
    # 2. Update record
    appointment.status = new_status
    appointment.save()
    
    # 3. Emit status changed event
    payload = {
        "appointment_id": appointment.id,
        "old_status": old_status,
        "new_status": new_status,
        "customer_id": appointment.customer.id,
        "customer_name": f"{appointment.customer.first_name} {appointment.customer.last_name}".strip(),
        "customer_phone": appointment.customer.phone,
        "staff_name": f"{appointment.staff.first_name} {appointment.staff.last_name}".strip(),
        "service_name": appointment.service.name,
        "price": float(appointment.service.price),
        "start_time": appointment.start_time.isoformat()
    }
    
    emit_event(
        event_type="appointment_status_changed",
        entity_type="appointment",
        entity_id=appointment.id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id
    )
    
    # 4. Emit specific helper event
    specific_events = {
        "confirmed": "appointment_confirmed",
        "arrived": "appointment_arrived",
        "in_service": "appointment_in_service",
        "completed": "appointment_completed",
        "cancelled": "appointment_cancelled",
        "no_show": "no_show_detected",
    }
    
    if new_status in specific_events:
        emit_event(
            event_type=specific_events[new_status],
            entity_type="appointment",
            entity_id=appointment.id,
            payload=payload,
            actor_type=actor_type,
            actor_id=actor_id
        )
        
    return appointment
