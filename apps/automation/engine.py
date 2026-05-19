import logging
from typing import Dict, Any, List
from django.apps import apps
from apps.notifications.manager import send_notification

logger = logging.getLogger(__name__)

def evaluate_conditions(conditions: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Evaluates rule conditions against an event payload.
    Simple key-value match engine.
    Example conditions: {"new_status": "cancelled"}
    Matches if payload has key "new_status" with value "cancelled".
    """
    if not conditions:
        return True
        
    for key, expected_value in conditions.items():
        if key not in payload:
            return False
            
        actual_value = payload[key]
        if actual_value != expected_value:
            return False
            
    return True


def execute_rule_actions(actions: List[Dict[str, Any]], payload: Dict[str, Any], event_entity_id: str) -> None:
    """
    Executes actions configured in an automation rule.
    Interpolates variables in messages using the event payload.
    """
    for action in actions:
        action_type = action.get("type")
        logger.info(f"⚙️ Running action [{action_type}]")
        
        # 1. Route: Send Telegram or SMS Notification
        if action_type in ["send_telegram_message", "send_sms", "send_notification"]:
            message_tpl = action.get("message", "")
            
            # Interpolate payload variables if any, e.g. "Hello {customer_name}"
            try:
                message = message_tpl.format(**payload)
            except Exception as e:
                logger.warning(f"⚠️ Failed to interpolate message: {str(e)}. Using raw template.")
                message = message_tpl
                
            # Extract recipient details from payload or config
            phone = payload.get("customer_phone")
            telegram_id = payload.get("telegram_id")
            
            # If the actor is not in the payload, look up customer/staff details
            if not phone and "customer_id" in payload:
                try:
                    Customer = apps.get_model("customers", "Customer")
                    cust = Customer.objects.get(id=payload["customer_id"])
                    phone = cust.phone
                    telegram_id = cust.telegram_id
                except Exception as e:
                    logger.error(f"❌ Failed to load customer for notification: {str(e)}")
                    
            if not phone and not telegram_id:
                logger.error("❌ Cannot send notification: phone and telegram_id are both missing.")
                continue
                
            # Trigger Notification Manager
            send_notification(
                recipient_phone=phone,
                message=message,
                telegram_id=telegram_id
            )
            
        # 2. Action: Update Customer Status
        elif action_type == "update_customer_status":
            new_status = action.get("status")
            customer_id = payload.get("customer_id")
            
            if customer_id and new_status:
                try:
                    Customer = apps.get_model("customers", "Customer")
                    cust = Customer.objects.get(id=customer_id)
                    cust.status = new_status
                    cust.save()
                    logger.info(f"👤 Updated customer #{customer_id} status to {new_status} via automation")
                except Exception as e:
                    logger.error(f"❌ Failed to update customer status: {str(e)}")
                    
        else:
            logger.warning(f"⚠️ Unknown action type: {action_type}")
