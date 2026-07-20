# Payments Package

O'zbekiston to'lov tizimlari uchun Django integratsiya paketi. Hozirda **Payme** va **Uzum Bank** qo'llab-quvvatlanadi.

## Qo'llab-quvvatlanadigan to'lov tizimlari

| Tizim | Merchant API (Webhook) | Client API | Dokumentatsiya |
|-------|----------------------|------------|----------------|
| **Payme** | 7 ta metod (JSON-RPC 2.0) | Karta, Kvitansiya, Subscribe | [PAYME.md](PAYME.md) |
| **Uzum Bank** | 5 ta metod (REST) | Checkout, Refund, Deeplink | [UZUM.md](UZUM.md) |

## Tezkor o'rnatish

### 1. Paketlar

```bash
pip install django djangorestframework requests environs
```

### 2. settings.py

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "payme",
    "uzum",
]
```

### 3. urls.py

```python
from django.urls import path, include

urlpatterns = [
    path("payme/", include("payme.urls")),   # POST /payme/update/
    path("uzum/", include("uzum.urls")),     # POST /uzum/{action}/
]
```

### 4. .env

```env
# ── Payme ─────────────────────────────────────
PAYME_ID=your-merchant-id
PAYME_KEY=your-merchant-key
PAYME_ACCOUNT_MODEL=orders.models.Order
PAYME_ACCOUNT_FIELD=order_id

# ── Uzum ──────────────────────────────────────
UZUM_USERNAME=your-login
UZUM_PASSWORD=your-password
UZUM_SERVICE_ID=12345
UZUM_ACCOUNT_MODEL=orders.models.Order
UZUM_ACCOUNT_FIELD=order_id
```

### 5. Migratsiya

```bash
python manage.py migrate
```

## Qanday ishlaydi

### Payme

```
Foydalanuvchi → Payme checkout → Payme server → POST /payme/update/ → Sizning server
```

- **Merchant API**: Payme sizga webhook yuboradi (CheckPerform → Create → Perform)
- **Subscribe API**: Siz Payme'ga karta token orqali to'lov yuborasiz
- **Protokol**: JSON-RPC 2.0, barcha javoblar HTTP 200

### Uzum Bank

```
Foydalanuvchi → Uzum ilovasi → Uzum server → POST /uzum/{action}/ → Sizning server
```

- **Merchant API**: Uzum sizga webhook yuboradi (check → create → confirm)
- **Checkout API**: Siz Uzum'ga karta to'lov so'rovi yuborasiz
- **Protokol**: REST POST, HTTP Basic Auth

## Callback handler'lar

Har ikkala tizimda ham to'lov hodisalarini boshqarish uchun view'ni override qilasiz:

```python
# Payme uchun
from payme.views.base import BasePaymeWebHookAPIView

class MyPaymeView(BasePaymeWebHookAPIView):
    def handle_successfully_payment(self, params, result, **kwargs):
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="paid")
```

```python
# Uzum uchun
from uzum.views.base import BaseUzumWebHookAPIView

class MyUzumView(BaseUzumWebHookAPIView):
    def handle_successfully_payment(self, params, result, **kwargs):
        Order.objects.filter(pk=params.get("order_id")).update(status="paid")
```

## To'liq dokumentatsiya

- **Payme**: [PAYME.md](PAYME.md) — Merchant API, Subscribe API, Karta API, Kvitansiya API, fiskal ma'lumotlar, xavfsizlik
- **Uzum Bank**: [UZUM.md](UZUM.md) — Merchant API, Checkout API, deeplink, fiskal ma'lumotlar, xavfsizlik

## Loyiha strukturasi

```
payments_package/
├── .env                    # Muhit o'zgaruvchilari (gitga tushmaydi)
├── manage.py
├── PAYME.md                # Payme dokumentatsiya
├── UZUM.md                 # Uzum dokumentatsiya
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── payme/                  # Payme to'lov app
│   ├── views/              # Webhook handler
│   ├── classes/            # Client (karta, kvitansiya, to'lov havolasi)
│   ├── models.py           # PaymeTransactions
│   └── ...
└── uzum/                   # Uzum to'lov app
    ├── views/              # Webhook handler
    ├── classes/            # Checkout API client
    ├── models.py           # UzumTransactions
    └── ...
```

## Xavfsizlik

- HTTP Basic Auth (ikkala tizimda)
- IP whitelist (Uzum — app darajasida, Payme — Nginx darajasida)
- Service ID / Merchant Key validatsiya
- Dublikat tranzaksiya himoyasi
- Summa validatsiya
- 3 tilli xato xabarlari (uz, ru, en)
- `.env` orqali maxfiy ma'lumotlar boshqaruvi
