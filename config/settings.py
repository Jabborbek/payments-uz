import os
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# Django core
# ──────────────────────────────────────────────
SECRET_KEY = env.str("SECRET_KEY", "change-me-in-production")
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["*"])
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ──────────────────────────────────────────────
# Installed apps
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "payme",
    "uzum",
]

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ──────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ──────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# Static files
# ──────────────────────────────────────────────
STATIC_URL = "static/"

# ──────────────────────────────────────────────
# Payme configuration — ALL values from .env
# ──────────────────────────────────────────────

# Merchant ID — Payme kabinetidan olinadi
PAYME_ID = env.str("PAYME_ID")

# Merchant API key — webhook autentifikatsiya uchun
PAYME_KEY = env.str("PAYME_KEY")

# Account model — to'lov bog'lanadigan Django model (masalan: "orders.models.Order")
PAYME_ACCOUNT_MODEL = env.str("PAYME_ACCOUNT_MODEL")

# Account field — account modelda qaysi field orqali to'lov aniqlash (masalan: "order_id")
PAYME_ACCOUNT_FIELD = env.str("PAYME_ACCOUNT_FIELD")

# Amount field — one-time payment uchun summani tekshiradigan field nomi
PAYME_AMOUNT_FIELD = env.str("PAYME_AMOUNT_FIELD", "amount")

# One-time payment — True bo'lsa, summa account modeldagi amount bilan solishtiriladi
PAYME_ONE_TIME_PAYMENT = env.bool("PAYME_ONE_TIME_PAYMENT", False)

# Test mode — True bo'lsa, test.paycom.uz ishlatiladi
PAYME_IS_TEST_MODE = env.bool("PAYME_IS_TEST_MODE", False)

# Fallback ID — fallback to'lov havolasi uchun (ixtiyoriy)
PAYME_FALLBACK_ID = env.str("PAYME_FALLBACK_ID", "")

# Admin panelda PaymeTransactions ko'rsatilmasin (ixtiyoriy)
PAYME_DISABLE_ADMIN = env.bool("PAYME_DISABLE_ADMIN", False)

# ──────────────────────────────────────────────
# Uzum configuration
# ──────────────────────────────────────────────

# Merchant API — webhook autentifikatsiya (Uzum kabinetidan olinadi)
UZUM_USERNAME = env.str("UZUM_USERNAME")
UZUM_PASSWORD = env.str("UZUM_PASSWORD")
UZUM_SERVICE_ID = env.int("UZUM_SERVICE_ID")

# Account model — to'lov bog'lanadigan Django model
UZUM_ACCOUNT_MODEL = env.str("UZUM_ACCOUNT_MODEL")

# Account field — params ichidagi qaysi field orqali buyurtma topiladi
UZUM_ACCOUNT_FIELD = env.str("UZUM_ACCOUNT_FIELD")

# Amount field — one-time payment uchun
UZUM_AMOUNT_FIELD = env.str("UZUM_AMOUNT_FIELD", "amount")

# One-time payment — True bo'lsa summani tekshiradi
UZUM_ONE_TIME_PAYMENT = env.bool("UZUM_ONE_TIME_PAYMENT", False)

# IP whitelist — faqat shu IP'lardan webhook qabul qilinadi (ixtiyoriy)
# Masalan: UZUM_ALLOWED_IPS=["1.2.3.4","5.6.7.8"]
_uzum_ips = env.str("UZUM_ALLOWED_IPS", "")
UZUM_ALLOWED_IPS = [ip.strip() for ip in _uzum_ips.split(",") if ip.strip()] or None

# Checkout API — karta orqali to'lov uchun (ixtiyoriy)
UZUM_TERMINAL_ID = env.str("UZUM_TERMINAL_ID", "")
UZUM_API_KEY = env.str("UZUM_API_KEY", "")
UZUM_ACCESS_TOKEN = env.str("UZUM_ACCESS_TOKEN", "")
UZUM_IS_TEST_MODE = env.bool("UZUM_IS_TEST_MODE", False)

# Admin panelda yashirish
UZUM_DISABLE_ADMIN = env.bool("UZUM_DISABLE_ADMIN", False)
