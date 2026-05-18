.PHONY: help d-up d-down d-build d-logs run-web run-bot migrate makemigrations su shell

# O'zgaruvchilar
PYTHON = python
MANAGE = $(PYTHON) manage.py

help:
	@echo "Boshqaruv buyruqlari ro'yxati:"
	@echo ""
	@echo "--- Docker buyruqlari ---"
	@echo "  make d-up             - Docker compose'ni orqa fonsiz ishga tushirish (detached)"
	@echo "  make d-down           - Docker compose'ni to'xtatish va o'chirish"
	@echo "  make d-build          - Docker image'larni qayta qurish"
	@echo "  make d-logs           - Docker loglarini ko'rish"
	@echo ""
	@echo "--- Django (Local) ---"
	@echo "  make run-web          - Django serverni ishga tushirish (127.0.0.1:8000)"
	@echo "  make migrate          - Ma'lumotlar bazasiga migratsiyalarni yozish"
	@echo "  make makemigrations   - Yangi migratsiya fayllarini yaratish"
	@echo "  make su               - Superuser yaratish"
	@echo "  make shell            - Django shell'ni ochish"
	@echo ""
	@echo "--- Aiogram Bot (Local) ---"
	@echo "  make run-bot          - Telegram botni ishga tushirish"
	@echo ""
	@echo "--- React Frontend ---"
	@echo "  make run-front        - React frontend ni ishga tushirish (Vite)"

# --- Docker ---
d-up:
	docker compose up -d

d-down:
	docker compose down

d-build:
	docker compose build

d-logs:
	docker compose logs -f

# --- Django ---
run-web:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

su:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

# --- Bot ---
run-bot:
	$(PYTHON) barber/bot.py

# --- Frontend ---
run-front:
	cd frontend && npm run dev
