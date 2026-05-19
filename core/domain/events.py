import logging
from typing import Any, Dict, Optional
from django.apps import apps
from django.utils import timezone

logger = logging.getLogger(__name__)

def emit_event(
    event_type: str,
    entity_type: str,
    entity_id: Any,
    payload: Dict[str, Any],
    actor_type: str = "system",
    actor_id: Optional[Any] = None
) -> Any:
    """
    Core function to emit a system/domain event.
    Logs event in DB, broadcasts to WebSockets, and schedules Celery task for automations.
    """
    try:
        # Prevent circular imports by importing models lazily
        Event = apps.get_model("events", "Event")
        
        # 1. Save Event in DB
        event = Event.objects.create(
            type=event_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            payload=payload,
            actor_type=actor_type,
            actor_id=str(actor_id) if actor_id else None,
            created_at=timezone.now()
        )
        
        logger.info(f"📣 Event emitted: [{event_type}] on {entity_type} #{entity_id}")
        
        # 2. Broadcast via Django Channels (WebSockets)
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    "live_metrics",
                    {
                        "type": "broadcast_event",
                        "event": {
                            "id": event.id,
                            "type": event.type,
                            "entity_type": event.entity_type,
                            "entity_id": event.entity_id,
                            "payload": event.payload,
                            "actor_type": event.actor_type,
                            "created_at": event.created_at.isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.warning(f"⚠️ Failed to broadcast event via WebSockets: {str(e)}")

        try:
            from apps.automation.tasks import execute_automation_rules_task
            execute_automation_rules_task.delay(event.id)
        except Exception as e:
            logger.error(f"❌ Failed to queue automation execution for event #{event.id}: {str(e)}")

        return event

    except Exception as e:
        logger.error(f"❌ Error emitting event: {str(e)}")
        raise e
