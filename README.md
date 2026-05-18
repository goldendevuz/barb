# Barbershop Telegram Bot 🪒

O'zbek tilidagi sartaroshxona Telegram bot loyihasi. Django admin + Aiogram 3.x.

## Texnologiyalar

| Qatlam | Texnologiya |
|--------|------------|
| Backend | Django 4.2 |
| Bot | Aiogram 3.x |
| Ma'lumotlar bazasi | SQLite |
| Konfiguratsiya | python-decouple |
| Python | 3.10+ |

## Loyiha tuzilishi

```
barb/
├── config/
│   ├── __init__.py
│   ├── settings.py       # Django sozlamalari
│   ├── urls.py           # URL marshrutlash
│   └── wsgi.py           # WSGI entry point
├── barber/
│   ├── __init__.py
│   ├── apps.py           # App konfiguratsiyasi
│   ├── models.py         # Database modellari
│   ├── admin.py          # Django admin panel
│   └── bot.py            # Telegram bot (Aiogram)
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## O'rnatish

```bash
# 1. Virtual muhit yaratish
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. .env faylini sozlash
cp .env.example .env
# .env faylini oching va TOKEN ni to'ldiring:
# TELEGRAM_BOT_TOKEN=your_real_token_here

# 4. Migratsiyalarni bajarish
python manage.py migrate

# 5. Superuser yaratish (admin/admin)
python manage.py createsuperuser
# Username: admin | Password: admin
```

## Ishga tushirish

### Django Admin
```bash
python manage.py runserver
# → http://127.0.0.1:8000/admin/
```

### Telegram Bot
```bash
# Alohida terminalni oching!
python barber/bot.py
```

## Muhit o'zgaruvchilari (.env)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here     # BotFather'dan olingan token
DJANGO_SECRET_KEY=your-secret-key          # Django maxfiy kalit
DEBUG=True                                  # Production'da False
```

## Bot buyruqlari

| Tugma | Tavsif |
|-------|--------|
| `/start` | Botni boshlash, asosiy menyu |
| 📅 Navbat olish | Yangi navbat olish (xizmat → sartarosh → sana → vaqt) |
| 📋 Mening navbatlarim | Barcha navbatlarni ko'rish |
| ❌ Navbatni bekor qilish | Faol navbatni bekor qilish |
| ℹ️ Ma'lumot | Sartaroshxona haqida |

## Database modellari

- **Barber** — Sartarosh (ism, telefon, faollik)
- **Service** — Xizmat (nom, narx, davomiylik)
- **Client** — Mijoz (telegram_id, ism, telefon)
- **Booking** — Buyurtma (mijoz, sartarosh, xizmat, sana, vaqt, narx, holat)

## Booking holatlari

| Holat | Ma'nosi |
|-------|---------|
| `pending` | ⏳ Kutilmoqda |
| `confirmed` | ✅ Tasdiqlangan |
| `cancelled` | ❌ Bekor qilingan |
| `done` | ✔️ Bajarilgan |

## Admin panel — demo ma'lumot qo'shish

Admin panelga kiring: http://127.0.0.1:8000/admin/

1. **Sartaroshlar** → "Qo'shish" → ism va telefon kiriting
2. **Xizmatlar** → "Qo'shish" → xizmat nomi, narx va davomiylik kiriting
3. Bot orqali navbat oling — **Buyurtmalar** bo'limida ko'rsatiladi

---

> **Eslatma:** Bot va Django server bir vaqtda ish vaqtida bo'lishi kerak.
> Bot alohida terminal oynasida ishga tushiriladi.
