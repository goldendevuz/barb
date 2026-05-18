from django.contrib import admin
from .models import Barber, Service, Client, Booking

admin.site.site_header = "🪒 Sartaroshxona Boshqaruvi"
admin.site.site_title = "Sartaroshxona Admin"
admin.site.index_title = "Bosh sahifa"


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'phone')
    list_editable = ('active',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('active',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram_id', 'phone', 'created_at')
    search_fields = ('name', 'phone', 'telegram_id')
    readonly_fields = ('telegram_id', 'created_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'service', 'date', 'time', 'price', 'status', 'created_at')
    list_filter = ('status', 'barber', 'date')
    search_fields = ('client__name', 'barber__name', 'service__name')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    ordering = ('-date', '-time')
