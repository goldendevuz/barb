"""
Demo ma'lumotlarni bazaga qo'shish uchun management command.
Ishlatish: python manage.py seed_demo
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from barber.models import Barber, Service

BARBERS = [
    {"name": "Jasur Karimov",  "phone": "+998 90 123-45-67"},
    {"name": "Bobur Yusupov",  "phone": "+998 91 234-56-78"},
    {"name": "Sherzod Aliyev", "phone": "+998 93 345-67-89"},
]

SERVICES = [
    {"name": "Soch olish",              "price": 25000,  "duration": 30},
    {"name": "Soqol olish",             "price": 15000,  "duration": 20},
    {"name": "Soch + Soqol",            "price": 35000,  "duration": 45},
    {"name": "Bolalar soch olish",      "price": 20000,  "duration": 25},
    {"name": "Soch bo'yash",            "price": 60000,  "duration": 60},
    {"name": "Massaj (bosh)",           "price": 30000,  "duration": 20},
]


def run():
    for b in BARBERS:
        obj, created = Barber.objects.get_or_create(name=b["name"], defaults={"phone": b["phone"]})
        print(f"{'✅ Yangi' if created else '⏭️  Mavjud'} sartarosh: {obj.name}")

    for s in SERVICES:
        obj, created = Service.objects.get_or_create(
            name=s["name"],
            defaults={"price": s["price"], "duration": s["duration"]},
        )
        print(f"{'✅ Yangi' if created else '⏭️  Mavjud'} xizmat: {obj.name} — {obj.price:,.0f} so'm")

    print("\n🎉 Demo ma'lumotlar muvaffaqiyatli qo'shildi!")
    print(f"   Sartaroshlar: {Barber.objects.count()} ta")
    print(f"   Xizmatlar:    {Service.objects.count()} ta")


if __name__ == "__main__":
    run()
