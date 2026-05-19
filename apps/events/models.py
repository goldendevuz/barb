from django.db import models

class Event(models.Model):
    type = models.CharField(max_length=100)  # e.g., appointment_created, no_show_detected
    entity_type = models.CharField(max_length=50)  # e.g., appointment, customer
    entity_id = models.CharField(max_length=50)  # Reference ID
    payload = models.JSONField(default=dict)  # JSON details
    actor_type = models.CharField(max_length=50, default="system")  # e.g., customer, staff, bot
    actor_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Event: {self.type} on {self.entity_type} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
