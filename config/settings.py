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
