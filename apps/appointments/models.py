from django.db import models
from apps.customers.models import Customer
from apps.staff.models import Staff
from apps.services.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("confirmed", "Confirmed"),
        ("arrived", "Arrived"),
        ("in_service", "In Service"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="appointments")
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_time"]),
        ]

    def __str__(self):
        return f"Appointment with {self.customer.first_name} by {self.staff.first_name} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"
