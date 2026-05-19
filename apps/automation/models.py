from django.db import models

class AutomationRule(models.Model):
    name = models.CharField(max_length=100)
    trigger = models.CharField(max_length=100, db_index=True)  # Event type, e.g., appointment_cancelled, payment_received
    conditions = models.JSONField(default=dict, blank=True, help_text="Filter conditions, e.g., {'new_status': 'cancelled'}")
    actions = models.JSONField(default=list, help_text="List of actions: [{'type': 'send_telegram_message', 'message': '...'}]")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Trigger: {self.trigger})"
