from django.db import models

class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("sms", "SMS"),
        ("telegram", "Telegram"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    
    recipient = models.CharField(max_length=100)  # Phone number or Telegram ID
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification to {self.recipient} via {self.channel} ({self.status})"
