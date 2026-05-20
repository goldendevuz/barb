"""
Project .env loader — barcha konfiguratsiya shu modul orqali o'qiladi.

Foydalanish:
    from core.envs import config, SECRET_KEY, TELEGRAM_BOT_TOKEN
"""
from pathlib import Path

from decouple import Config, Csv, RepositoryEnv

# barb/ (loyiha ildizi)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.is_file():
    config = Config(RepositoryEnv(str(ENV_PATH)))
else:
    from decouple import config  # noqa: F401 — OS env (Docker env_file)

# =========================
# CORE SECURITY SETTINGS
# =========================

SECRET_KEY = config(
    "SECRET_KEY",
    default=config("DJANGO_SECRET_KEY", default="insecure-default-secret-key-change-in-production"),
)

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://127.0.0.1",
    cast=Csv(),
)

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://127.0.0.1",
    cast=Csv(),
)

# =========================
# DATABASE
# =========================

DB_HOST = config("DB_HOST", default="db")
DB_PORT = config("DB_PORT", default=5432, cast=int)
DB_USER = config("DB_USER", default="barber")
DB_PASSWORD = config("DB_PASSWORD", default="barber")
DB_NAME = config("DB_NAME", default="barber")

DB_URL = config(
    "DB_URL",
    default=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# =========================
# REDIS / CELERY
# =========================

REDIS_URL = config("REDIS_URL", default="redis://redis:6379/1")

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)

# =========================
# TOKENS / EXTERNAL SERVICES
# =========================

TELEGRAM_BOT_TOKEN = config(
    "TELEGRAM_BOT_TOKEN",
    default=config("BOT_TOKEN", default=""),
)

TELEGRAM_BOT_USERNAME = config(
    "TELEGRAM_BOT_USERNAME",
    default=config("BOT_USERNAME", default=""),
)

API_BASE_URL = config(
    "API_BASE_URL",
    default=config("API_BASE", default="http://web:8000/api/"),
)

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="").replace("-", " ")

SMS_TOKEN = config("SMS_TOKEN", default="")
SMS_URL = config("SMS_URL", default="")

BOT_OWNER_IDS = config("BOT_OWNER_IDS", default="")

# =========================
# BUSINESS SETTINGS
# =========================

API_V1_URL = config("API_V1_URL", default="/api/v1/")

ACCESS_TOKEN_LIFETIME = config("ACCESS_TOKEN_LIFETIME", default=15, cast=int)
REFRESH_TOKEN_LIFETIME = config("REFRESH_TOKEN_LIFETIME", default=1, cast=int)

TIME_ZONE = config("TIME_ZONE", default="Asia/Tashkent")

ADMIN_URL = config("ADMIN_URL", default="admin/")
SHOP_CREATE_PATH = config("SHOP_CREATE_PATH", default="/shops/create/")
PART_CREATE_PATH = config("PART_CREATE_PATH", default="/parts/create/")
