from django.db import models
from django.contrib.auth.models import User

class Barbershop(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    ROLE_CHOICES = [
        ("barber", "Barber"),
        ("receptionist", "Receptionist"),
        ("admin", "Admin"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_profile")
    barbershop = models.ForeignKey(Barbershop, on_delete=models.CASCADE, null=True, blank=True, related_name="staff")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="barber")
    telegram_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        branch = f" @ {self.barbershop.name}" if self.barbershop else ""
        return f"{self.first_name} {self.last_name} ({self.get_role_display()}){branch}".strip()


class BarberSchedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    is_working = models.BooleanField(default=True)
    start_time = models.TimeField(default="09:00:00")
    end_time = models.TimeField(default="18:00:00")

    class Meta:
        unique_together = ("staff", "date")

    def __str__(self):
        status = "Ishlaydi" if self.is_working else "Ishlamaydi"
        return f"{self.staff} on {self.date}: {status} ({self.start_time} - {self.end_time})"

