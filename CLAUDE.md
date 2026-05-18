# CLAUDE.md

## 1. Project Summary

O'zbek tilidagi sartaroshxona Telegram boti. Mijozlar navbat oladi (xizmat → sartarosh → sana → vaqt → tasdiqlash), buyurtmalarini ko'radi va bekor qiladi. Django admin orqali sartaroshlar, xizmatlar va buyurtmalar boshqariladi.

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Web Framework | Django 4.2 |
| Bot Framework | Aiogram 3.x (FSM, inline keyboards) |
| Database | SQLite (db.sqlite3) |
| Config | python-decouple (.env) |
| Hosting | Local / any Linux server |
| External APIs | Telegram Bot API |

---

## 3. Folder Structure

```
/
├── config/           # Django project settings, urls, wsgi
├── barber/           # Main app: models, admin, bot
│   ├── models.py     # Barber, Service, Client, Booking
│   ├── admin.py      # Django admin panel config
│   └── bot.py        # Aiogram 3 Telegram bot (entry point)
├── manage.py         # Django CLI
├── requirements.txt
└── .env              # Secret keys (gitignored)
```

---

## 4. Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=   # BotFather'dan olingan token
DJANGO_SECRET_KEY=    # Django maxfiy kalit

# Optional
DEBUG=True            # Production'da False qo'yish kerak
```

---

## 5. Running the Project

```bash
# O'rnatish
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # tokenni to'ldiring

# Migratsiya
python manage.py migrate
python manage.py createsuperuser  # admin/admin

# Django admin (terminal 1)
python manage.py runserver        # → http://127.0.0.1:8000/admin/

# Telegram bot (terminal 2)
python barber/bot.py
```

---

## 6. Conventions & Patterns

- Django models: O'zbek `verbose_name` barcha fieldlarda
- Bot handlers: `@sync_to_async` orqali Django ORM'ni async'dan chaqirish
- FSM: `BookingState` states — contact → service → barber → date → time → confirm
- Inline keyboards: `callback_data` format — `"type:id"` (masalan `"service:3:15000"`)
- Back navigation: `"back:destination"` callback pattern

---

## 7. Important Notes

- **Bot va Django alohida prosesslarda ishlaydi** — ikki terminal oynasi kerak
- **`@sync_to_async`** — barcha Django ORM chaqiruvlari bot.py'da shu decorator orqali
- **`sys.path.insert(0, ...)`** — bot.py Django'ni topishi uchun path manually set qilingan
- Admin panel: `http://127.0.0.1:8000/admin/` — username: admin, password: admin
- Bot birinchi `/start` da Client yaratadi; telefon raqam birinchi navbatda so'raladi
- Booking `status` fieldini faqat admin paneldan o'zgartirish mumkin

---

## Behavioral Guidelines

> 🤖 `sonnet` · 🎯 🔴 `high` · ⚙️ Multi-file project creation

### Hard rules
- **NEVER `git push --force`** to main/master
- **NEVER `git reset --hard`** with uncommitted changes
- Touch only what the user asks — surgical changes only
- Surface tradeoffs before implementing
