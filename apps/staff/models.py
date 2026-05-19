from django.db import models

class Staff(models.Model):
    ROLE_CHOICES = [
        ("barber", "Barber"),
        ("receptionist", "Receptionist"),
        ("admin", "Admin"),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="barber")
    telegram_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})".strip()
