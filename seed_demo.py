import os
import django
import sys
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from apps.staff.models import Staff, Barbershop, BarberSchedule
from apps.services.models import Service
from apps.automation.models import AutomationRule

BARBERSHOPS = [
    {
        "name": "Chilonzor Filiali",
        "address": "Toshkent sh., Lutfiy ko'chasi, 24-uy",
        "latitude": 41.278385,
        "longitude": 69.202356
    },
    {
        "name": "Yunusobod Filiali",
        "address": "Toshkent sh., Amir Temur ko'chasi, 82-uy",
        "latitude": 41.364256,
        "longitude": 69.287842
    }
]

STAFF = [
    {"first_name": "Jasur", "last_name": "Karimov", "phone": "+998901234567", "role": "barber", "username": "jasur_barber"},
    {"first_name": "Bobur", "last_name": "Yusupov", "phone": "+998912345678", "role": "barber", "username": "bobur_barber"},
    {"first_name": "Sherzod", "last_name": "Aliyev", "phone": "+998933456789", "role": "admin", "username": "sherzod_admin"},
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
                "message": "👋 Assalomu alaykum {customer_name}! Sizning buyurtmangiz muvaffaqiyatli qabul qilindi.\n\n🏢 Filial: {barbershop_name}\n💇‍♂️ Usta: {staff_name}\n💆‍♂️ Xizmat: {service_name}\n⏰ Vaqt: {start_time}\n\nSizni kutib qolamiz!"
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
    print("🚀 Seeding Barber CRM Multi-Tenant SaaS...")
    
    # 1. Seed Barbershops
    branches = []
    for bs in BARBERSHOPS:
        obj, created = Barbershop.objects.get_or_create(
            name=bs["name"],
            defaults={"address": bs["address"], "latitude": bs["latitude"], "longitude": bs["longitude"]}
        )
        branches.append(obj)
        print(f"  🏢 Barbershop branch: {obj.name} @ {obj.address}")

    # 2. Seed Users & Staff
    staff_count = 0
    today = date.today()
    for idx, s in enumerate(STAFF):
        # Create standard auth user for barber
        user, u_created = User.objects.get_or_create(
            username=s["username"],
            defaults={
                "first_name": s["first_name"],
                "last_name": s["last_name"],
                "email": f"{s['username']}@barbercrm.uz"
            }
        )
        if u_created:
            user.set_password("barberpass123")
            user.save()
            print(f"  👤 Auth user created: {user.username}")

        # Choose a branch
        branch = branches[idx % len(branches)]

        obj, created = Staff.objects.get_or_create(
            phone=s["phone"],
            defaults={
                "user": user,
                "barbershop": branch,
                "first_name": s["first_name"],
                "last_name": s["last_name"],
                "role": s["role"]
            }
        )
        if created:
            staff_count += 1
            print(f"  💇‍♂️ Staff created: {obj.first_name} {obj.last_name} in {branch.name}")

            # 3. Seed work schedule for this barber (next 7 days)
            if s["role"] == "barber":
                for day_offset in range(7):
                    sched_date = today + timedelta(days=day_offset)
                    BarberSchedule.objects.get_or_create(
                        staff=obj,
                        date=sched_date,
                        defaults={
                            "is_working": True,
                            "start_time": "09:00:00",
                            "end_time": "18:00:00"
                        }
                    )
                print(f"    📅 Schedule filled for {obj.first_name} (next 7 days)")

    # 4. Seed Services
    service_count = 0
    for sv in SERVICES:
        # Register service in both branches
        for branch in branches:
            obj, created = Service.objects.get_or_create(
                name=f"{sv['name']} ({branch.name.split()[0]})",
                barbershop=branch,
                defaults={"price": sv["price"], "duration_minutes": sv["duration_minutes"]}
            )
            if created:
                service_count += 1
                print(f"  💆‍♂️ Service created: {obj.name} ({obj.price} UZS)")
            
    # 5. Seed Automation Rules
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
    print(f"  Added {len(branches)} branches, {staff_count} staff with schedules, {service_count} services, and {rule_count} automation rules.")

if __name__ == "__main__":
    seed()
