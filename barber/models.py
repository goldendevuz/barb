from django.db import models


class Barber(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ism")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sartarosh"
        verbose_name_plural = "Sartaroshlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Xizmat nomi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx (so'm)")
    duration = models.PositiveIntegerField(verbose_name="Davomiyligi (daqiqa)")
    active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.price:,.0f} so'm"


class Client(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    name = models.CharField(max_length=150, verbose_name="Ism")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.telegram_id})"


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_PENDING, '⏳ Kutilmoqda'),
        (STATUS_CONFIRMED, '✅ Tasdiqlangan'),
        (STATUS_CANCELLED, '❌ Bekor qilingan'),
        (STATUS_DONE, '✔️ Bajarilgan'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Mijoz", related_name='bookings')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, verbose_name="Sartarosh", related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Xizmat", related_name='bookings')
    date = models.DateField(verbose_name="Sana")
    time = models.TimeField(verbose_name="Vaqt")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="Holat")
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.client.name} → {self.barber.name} | {self.date} {self.time}"
