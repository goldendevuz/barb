import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.staff.models import Staff
from apps.services.models import Service
from apps.automation.models import AutomationRule

STAFF = [
    {"first_name": "Jasur", "last_name": "Karimov", "phone": "+998901234567", "role": "barber"},
    {"first_name": "Bobur", "last_name": "Yusupov", "phone": "+998912345678", "role": "barber"},
    {"first_name": "Sherzod", "last_name": "Aliyev", "phone": "+998933456789", "role": "admin"},
]

SERVICES = [
    {"name": "Soch olish (Classic)", "price": 40000.00, "duration_minutes": 30},
    {"name": "Soqol tarash", "price": 20000.00, "duration_minutes": 20},
    {"name": "Soch va Soqol (Kombinatsiya)", "price": 50000.00, "duration_minutes": 45},
    {"name": "Premium Massaj va Spa", "price": 120000.00, "duration_minutes": 60},
]

AUTOMATION_RULES = [
    {
        "name": "Yangi Bandlik Xabarnomasi",
        "trigger": "appointment_created",
        "conditions": {},
        "actions": [
            {
                "type": "send_telegram_message",
                "message": "👋 Assalomu alaykum {customer_name}! Sizning buyurtmangiz muvaffaqiyatli qabul qilindi.\n\n💇‍♂️ Usta: {staff_name}\n💆‍♂️ Xizmat: {service_name}\n⏰ Vaqt: {start_time}\n\nSizni kutib qolamiz!"
            }
        ]
    },
    {
        "name": "Bandlik Bekor Qilinganligi",
        "trigger": "appointment_cancelled",
        "conditions": {},
        "actions": [
            {
                "type": "send_telegram_message",
                "message": "❌ Hurmatli {customer_name}! Sizning #{appointment_id} raqamli bandligingiz bekor qilindi. Biron bir xato yuz bergan bo'lsa, usta bilan bog'laning."
            }
        ]
    },
    {
        "name": "VIP Mijoz Statusini O'rnatish",
        "trigger": "payment_received",
        "conditions": {"amount": 120000.00},
        "actions": [
            {
                "type": "update_customer_status",
                "status": "vip"
            },
            {
                "type": "send_telegram_message",
                "message": "🎉 Qadrli {customer_name}, premium xizmatimizdan foydalanganingiz uchun tashakkur! Sizga VIP mijoz maqomi berildi!"
            }
        ]
    }
]

def seed():
    print("🚀 Seeding Barber CRM SaaS...")
    
    # 1. Seed Staff
    staff_count = 0
    for s in STAFF:
        obj, created = Staff.objects.get_or_create(
            phone=s["phone"],
            defaults={"first_name": s["first_name"], "last_name": s["last_name"], "role": s["role"]}
        )
        if created:
            staff_count += 1
            print(f"  💇‍♂️ Staff created: {obj.first_name} {obj.last_name}")
            
    # 2. Seed Services
    service_count = 0
    for sv in SERVICES:
        obj, created = Service.objects.get_or_create(
            name=sv["name"],
            defaults={"price": sv["price"], "duration_minutes": sv["duration_minutes"]}
        )
        if created:
            service_count += 1
            print(f"  💆‍♂️ Service created: {obj.name} ({obj.price} UZS)")
            
    # 3. Seed Automation Rules
    rule_count = 0
    for r in AUTOMATION_RULES:
        obj, created = AutomationRule.objects.get_or_create(
            name=r["name"],
            defaults={"trigger": r["trigger"], "conditions": r["conditions"], "actions": r["actions"]}
        )
        if created:
            rule_count += 1
            print(f"  ⚙️ Automation Rule created: {obj.name}")
            
    print(f"\n🎉 Seeding finished successfully!")
    print(f"  Added {staff_count} staff, {service_count} services, and {rule_count} automation rules.")

if __name__ == "__main__":
    seed()
