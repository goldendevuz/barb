from django.db import models
from apps.staff.models import Barbershop

class Service(models.Model):
    barbershop = models.ForeignKey(Barbershop, on_delete=models.CASCADE, null=True, blank=True, related_name="services")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.price} UZS)"

