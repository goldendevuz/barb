"""
.env yuklash: avval fayl, keyin OS muhit (Docker env_file).
Barcha sozlamalar os.environ orqali o'qiladi.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def _manual_load_env_file(path: Path) -> None:
    """python-dotenv bo'lmasa — oddiy .env parser."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        # Mavjud OS o'zgaruvchisini ustiga yozmaymiz (Docker env_file ustun)
        os.environ.setdefault(key, value)


def load_env() -> Path:
    """Loyiha .env faylini os.environ ga yuklaydi. Bir necha marta chaqirish xavfsiz."""
    if ENV_PATH.is_file():
        try:
            from dotenv import load_dotenv

            load_dotenv(ENV_PATH, override=False, encoding="utf-8")
        except ImportError:
            _manual_load_env_file(ENV_PATH)
    return ENV_PATH


# Modul import bo'lganda darhol yuklash
load_env()


def _strip(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def get_str(*keys: str, default: str = "") -> str:
    for key in keys:
        val = _strip(os.environ.get(key))
        if val:
            return val
    return default


def get_bool(key: str, default: bool = False) -> bool:
    val = _strip(os.environ.get(key))
    if not val:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def get_int(key: str, default: int = 0) -> int:
    val = _strip(os.environ.get(key))
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def get_csv(key: str, default: str = "*") -> list[str]:
    val = get_str(key, default=default)
    return [part.strip() for part in val.split(",") if part.strip()]


def _normalize_origin(url: str) -> str:
    """CSRF_TRUSTED_ORIGINS uchun scheme bo'lishi shart (https://host)."""
    url = url.strip()
    if not url or url == "*":
        return url
    if url.startswith(("http://", "https://")):
        return url.rstrip("/")
    return f"https://{url}".rstrip("/")


# =========================
# CORE SECURITY
# =========================

SECRET_KEY = get_str(
    "SECRET_KEY",
    "DJANGO_SECRET_KEY",
    default="insecure-default-secret-key-change-in-production",
)

DEBUG = get_bool("DEBUG", default=False)

ALLOWED_HOSTS = get_csv("ALLOWED_HOSTS", default="*")

CSRF_TRUSTED_ORIGINS = [
    _normalize_origin(o) for o in get_csv("CSRF_TRUSTED_ORIGINS", default="http://127.0.0.1")
]

CORS_ALLOWED_ORIGINS = [
    _normalize_origin(o) for o in get_csv("CORS_ALLOWED_ORIGINS", default="http://127.0.0.1")
]

# =========================
# DATABASE
# =========================

DB_HOST = get_str("DB_HOST", default="db")
DB_PORT = get_int("DB_PORT", default=5432)
DB_USER = get_str("DB_USER", default="barber")
DB_PASSWORD = get_str("DB_PASSWORD", default="barber")
DB_NAME = get_str("DB_NAME", default="barber")

DB_URL = get_str(
    "DB_URL",
    default=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# =========================
# REDIS / CELERY
# =========================

REDIS_URL = get_str("REDIS_URL", default="redis://redis:6379/1")

CELERY_BROKER_URL = get_str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = get_str("CELERY_RESULT_BACKEND", default=REDIS_URL)

# =========================
# TOKENS / EXTERNAL
# =========================

TELEGRAM_BOT_TOKEN = get_str("TELEGRAM_BOT_TOKEN", "BOT_TOKEN")

TELEGRAM_BOT_USERNAME = get_str("TELEGRAM_BOT_USERNAME", "BOT_USERNAME")

API_BASE_URL = get_str("API_BASE_URL", "API_BASE", default="http://web:8000/api/")

EMAIL_HOST_USER = get_str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_str("EMAIL_HOST_PASSWORD").replace("-", " ")

SMS_TOKEN = get_str("SMS_TOKEN")
SMS_URL = get_str("SMS_URL")

BOT_OWNER_IDS = get_str("BOT_OWNER_IDS")

# =========================
# BUSINESS
# =========================

API_V1_URL = get_str("API_V1_URL", default="/api/v1/")

ACCESS_TOKEN_LIFETIME = get_int("ACCESS_TOKEN_LIFETIME", default=15)
REFRESH_TOKEN_LIFETIME = get_int("REFRESH_TOKEN_LIFETIME", default=1)

TIME_ZONE = get_str("TIME_ZONE", default="Asia/Tashkent")

ADMIN_URL = get_str("ADMIN_URL", default="admin/")
SHOP_CREATE_PATH = get_str("SHOP_CREATE_PATH", default="/shops/create/")
PART_CREATE_PATH = get_str("PART_CREATE_PATH", default="/parts/create/")


def env_debug_summary() -> dict:
    """Ishga tushganda .env yuklanganini tekshirish uchun."""
    return {
        "env_path": str(ENV_PATH),
        "env_file_exists": ENV_PATH.is_file(),
        "debug": DEBUG,
        "secret_key_set": bool(SECRET_KEY) and not SECRET_KEY.startswith("insecure"),
        "telegram_token_set": bool(TELEGRAM_BOT_TOKEN),
        "db_host": DB_HOST,
        "allowed_hosts": ALLOWED_HOSTS,
        "csrf_trusted_origins": CSRF_TRUSTED_ORIGINS,
    }
