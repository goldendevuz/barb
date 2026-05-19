import logging
from celery import shared_task
from django.apps import apps
from .models import AutomationRule
from .engine import evaluate_conditions, execute_rule_actions

logger = logging.getLogger(__name__)

@shared_task
def execute_automation_rules_task(event_id: int):
    """
    Celery task that loads an Event, queries matching active rules,
    evaluates their conditions, and runs their configured actions.
    """
    try:
        Event = apps.get_model("events", "Event")
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        logger.error(f"Event #{event_id} not found. Automation aborted.")
        return
        
    logger.info(f"⚙️ Running automations for event #{event.id} [{event.type}]")
    
    # Query active automation rules matching the event type
    rules = AutomationRule.objects.filter(trigger=event.type, is_active=True)
    
    matched_count = 0
    for rule in rules:
        try:
            # 1. Evaluate conditions
            if evaluate_conditions(rule.conditions, event.payload):
                logger.info(f"🎯 Rule '{rule.name}' matched event #{event.id}!")
                
                # 2. Execute actions
                execute_rule_actions(rule.actions, event.payload, event.entity_id)
                matched_count += 1
            else:
                logger.debug(f"⏭️ Rule '{rule.name}' conditions did not match.")
        except Exception as e:
            logger.error(f"❌ Error running automation rule '{rule.name}': {str(e)}")
            
    logger.info(f"⚙️ Automations finished for event #{event.id}. Matched rules: {matched_count}/{rules.count()}")
