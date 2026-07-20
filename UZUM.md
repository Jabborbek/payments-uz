# Uzum Bank API — To'liq Dokumentatsiya

## Mundarija

1. [Umumiy ma'lumot](#umumiy-malumot)
2. [O'rnatish](#ornatish)
3. [Sozlash (.env)](#sozlash)
4. [Loyiha strukturasi](#loyiha-strukturasi)
5. [Merchant API (Webhook)](#merchant-api)
   - [CHECK](#check)
   - [CREATE](#create)
   - [CONFIRM](#confirm)
   - [REVERSE](#reverse)
   - [STATUS](#status)
6. [Checkout API (Client)](#checkout-api)
   - [register_payment](#register_payment)
   - [get_order_status](#get_order_status)
   - [refund](#refund)
   - [reverse](#reverse-checkout)
   - [complete](#complete)
   - [get_bindings](#get_bindings)
   - [get_receipts](#get_receipts)
7. [Tranzaksiya holatlari](#tranzaksiya-holatlari)
8. [Xato kodlari](#xato-kodlari)
9. [Xavfsizlik](#xavfsizlik)
10. [Callback handler'lar](#callback-handlerlar)
11. [Deeplink yaratish](#deeplink-yaratish)
12. [Fiskal ma'lumotlar](#fiskal-malumotlar)
13. [Django Admin](#django-admin)
14. [Ma'lumotlar bazasi](#malumotlar-bazasi)
15. [Amaliy misol](#amaliy-misol)

---

## Umumiy ma'lumot

Bu app [Uzum Bank](https://uzumbank.uz) to'lov tizimi bilan integratsiya qilish uchun Django REST Framework asosida yozilgan yechim. Ikki API qo'llab-quvvatlanadi:

- **Merchant API (Webhook)** — Uzum sizning serveringizga so'rov yuboradi (5 ta metod)
- **Checkout API (Client)** — Siz Uzum serveriga so'rov yuborasiz (karta orqali to'lov)

### Merchant API vs Checkout API

| Jihat | Merchant API | Checkout API |
|-------|-------------|-------------|
| **Yo'nalish** | Uzum → Siz | Siz → Uzum |
| **Foydalanish** | Uzum ilovasi orqali to'lov | Karta orqali to'lov (Visa, MC, Uzcard, Humo) |
| **Auth** | HTTP Basic Auth | X-Terminal-Id + X-API-Key |
| **Protokol** | REST POST | REST POST |
| **Endpoint** | Siz ochib berasiz | Uzum beradi |

---

## O'rnatish

### 1. Django settings.py

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "uzum",
]
```

### 2. URL sozlash

```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    path("uzum/", include("uzum.urls")),
]
```

Bu quyidagi endpointlarni yaratadi:
```
POST /uzum/check/
POST /uzum/create/
POST /uzum/confirm/
POST /uzum/reverse/
POST /uzum/status/
```

### 3. Migratsiya

```bash
python manage.py migrate
```

---

## Sozlash

### .env fayli

```env
# ── Uzum Merchant API (webhook) ───────────────
UZUM_USERNAME=your-uzum-login
UZUM_PASSWORD=your-uzum-password
UZUM_SERVICE_ID=12345
UZUM_ACCOUNT_MODEL=orders.models.Order
UZUM_ACCOUNT_FIELD=order_id
UZUM_AMOUNT_FIELD=amount
UZUM_ONE_TIME_PAYMENT=True

# IP whitelist (vergul bilan ajratilgan, bo'sh = tekshirilmaydi)
UZUM_ALLOWED_IPS=

# ── Uzum Checkout API (karta to'lov) ──────────
UZUM_TERMINAL_ID=your-terminal-uuid
UZUM_API_KEY=your-api-key
UZUM_ACCESS_TOKEN=your-jwt-token
UZUM_IS_TEST_MODE=True

# Admin panel
UZUM_DISABLE_ADMIN=False
```

### Sozlamalar tavsifi

| Sozlama | Turi | Majburiy | Tavsif |
|---------|------|----------|--------|
| `UZUM_USERNAME` | `str` | Ha | Webhook login (Uzum kabinetidan) |
| `UZUM_PASSWORD` | `str` | Ha | Webhook parol (Uzum kabinetidan) |
| `UZUM_SERVICE_ID` | `int` | Ha | Xizmat ID raqami |
| `UZUM_ACCOUNT_MODEL` | `str` | Ha | Buyurtma modeli (`"app.models.Model"`) |
| `UZUM_ACCOUNT_FIELD` | `str` | Ha | `params` ichidagi buyurtma field nomi |
| `UZUM_AMOUNT_FIELD` | `str` | Yo'q | Summa field nomi (default: `amount`) |
| `UZUM_ONE_TIME_PAYMENT` | `bool` | Yo'q | Summani tekshirish (default: `False`) |
| `UZUM_ALLOWED_IPS` | `str` | Yo'q | IP whitelist, vergul bilan (Uzum kabinetidan oling) |
| `UZUM_TERMINAL_ID` | `str` | Checkout uchun | Terminal UUID |
| `UZUM_API_KEY` | `str` | Checkout uchun | API kalit |
| `UZUM_ACCESS_TOKEN` | `str` | Checkout uchun | JWT token |
| `UZUM_IS_TEST_MODE` | `bool` | Yo'q | Test rejim (default: `False`) |

---

## Loyiha strukturasi

```
uzum/
├── __init__.py               # Uzum client eksport
├── admin.py                  # Django admin
├── apps.py                   # AppConfig
├── const.py                  # Statuslar, PayType, ViewType
├── models.py                 # UzumTransactions model
├── urls.py                   # Webhook endpointlar
├── util.py                   # Vaqt konvertatsiya
├── classes/
│   ├── client.py             # Checkout API client
│   └── http.py               # HTTP client
├── exceptions/
│   └── merchant.py           # Xato kodlari (3 tilda)
├── migrations/
│   └── 0001_initial.py
└── views/
    ├── base.py               # Asosiy webhook logic
    └── merchant.py           # Override qilinadigan view
```

---

## Merchant API

Uzum sizning serveringizga so'rov yuboradi. Barcha javoblar HTTP **200** qaytaradi.

### Autentifikatsiya

Uzum har bir so'rovda **HTTP Basic Auth** yuboradi:

```
Authorization: Basic base64(username:password)
```

App buni `UZUM_USERNAME` va `UZUM_PASSWORD` bilan tekshiradi.

---

### CHECK

Buyurtma mavjudligini tekshiradi. Uzum to'lov qilishdan oldin chaqiradi.

**So'rov (Uzum → Siz):**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "params": {
        "order_id": "123"
    }
}
```

**Muvaffaqiyatli javob:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "status": "OK",
    "data": {
        "account": {
            "value": "123"
        }
    }
}
```

**Xato javob:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "status": "FAILED",
    "errorCode": 10008
}
```

---

### CREATE

Tranzaksiya yaratadi. Buyurtma `PENDING` holatiga o'tadi.

**So'rov:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "transId": "uzum_abc123",
    "amount": 10000000,
    "params": {
        "order_id": "123"
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `serviceId` | `int` | Xizmat ID |
| `timestamp` | `int` | Unix vaqt (ms) |
| `transId` | `string` | Uzum tranzaksiya ID (unikal) |
| `amount` | `int` | Summa **tiyinda** (1 so'm = 100 tiyin) |
| `params` | `object` | Buyurtma identifikatori |

**Muvaffaqiyatli javob:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "status": "CREATED",
    "transTime": 1700000000000,
    "transId": "uzum_abc123",
    "amount": 10000000
}
```

**Muhim qoidalar:**
- Bir xil `transId` bilan qayta so'rov — mavjud tranzaksiya qaytariladi (idempotent)
- Allaqachon to'langan tranzaksiya uchun `10007` xato
- Bekor qilingan tranzaksiya uchun `10009` xato
- `UZUM_ONE_TIME_PAYMENT=True` bo'lsa summa tekshiriladi

---

### CONFIRM

To'lovni tasdiqlaydi. Tranzaksiya `PAID` holatiga o'tadi.

**So'rov:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "transId": "uzum_abc123"
}
```

**Muvaffaqiyatli javob:**
```json
{
    "serviceId": 12345,
    "transId": "uzum_abc123",
    "status": "CONFIRMED",
    "confirmTime": 1700000000000
}
```

---

### REVERSE

Tranzaksiyani bekor qiladi. Tranzaksiya `CANCELED` holatiga o'tadi.

**So'rov:**
```json
{
    "serviceId": 12345,
    "timestamp": 1700000000000,
    "transId": "uzum_abc123"
}
```

**Muvaffaqiyatli javob:**
```json
{
    "serviceId": 12345,
    "transId": "uzum_abc123",
    "status": "REVERSED",
    "reverseTime": 1700000000000,
    "amount": 10000000
}
```

---

### STATUS

Tranzaksiya holatini so'raydi.

**So'rov:**
```json
{
    "serviceId": 12345,
    "transId": "uzum_abc123"
}
```

**Javob:**
```json
{
    "serviceId": 12345,
    "transId": "uzum_abc123",
    "status": "CONFIRMED"
}
```

Mumkin bo'lgan statuslar: `CREATED`, `CONFIRMED`, `REVERSED`

---

## Checkout API

Karta orqali to'lov uchun **siz Uzum'ga** so'rov yuborasiz.

### Client yaratish

```python
from uzum import Uzum

uzum = Uzum(
    terminal_id="your-terminal-uuid",
    api_key="your-api-key",
    access_token="your-jwt-token",
    is_test_mode=True,
)
```

---

### register_payment

To'lov yaratish va foydalanuvchini to'lov sahifasiga yo'naltirish.

```python
result = uzum.register_payment(
    order_number="order-42",
    amount=150000,                                # tiyinda
    return_url="https://example.com/success",
    failure_url="https://example.com/failure",
    callback_url="https://example.com/callback",
    pay_type="ONE_STEP",                          # yoki "TWO_STEP"
    view_type="REDIRECT",                         # yoki "WEB_VIEW", "IFRAME"
    session_timeout=600,                          # 600-1800 sekund
    cart={                                         # Fiskal ma'lumotlar (ixtiyoriy)
        "cartId": "cart-1",
        "receiptType": "PURCHASE",
        "items": [{
            "title": "Mahsulot nomi",
            "productId": "prod-1",
            "quantity": 1,
            "unitPrice": 150000,
            "total": 150000,
            "spic": "12345678901234567",
            "packageCode": "123456",
            "vatPercent": 12,
        }]
    },
)

order_id = result["orderId"]
redirect_url = result["paymentRedirectUrl"]
# Foydalanuvchini redirect_url ga yo'naltiring
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `order_number` | `str` | Buyurtma raqami (unikal) |
| `amount` | `int` | Summa tiyinda |
| `return_url` | `str` | Muvaffaqiyatli to'lovdan keyin qaytish URL |
| `failure_url` | `str` | Muvaffaqiyatsiz to'lovdan keyin URL |
| `callback_url` | `str` | Server-to-server callback URL |
| `pay_type` | `str` | `ONE_STEP` (bir martalik) yoki `TWO_STEP` (hold → complete) |
| `view_type` | `str` | `REDIRECT`, `WEB_VIEW`, yoki `IFRAME` |
| `cart` | `dict` | Fiskal kvitansiya uchun tovar ma'lumotlari |

### To'lov turlari

| Tur | Tavsif |
|-----|--------|
| `ONE_STEP` | Bir bosqichda to'lov — avtomatik debit + fiskal chek |
| `TWO_STEP` | Ikki bosqichli — avval hold (AUTHORIZED), keyin `complete` yoki `reverse` |

---

### get_order_status

To'lov holatini tekshirish.

```python
result = uzum.get_order_status(order_id="uuid-order-id")
# result["status"]  →  "REGISTERED", "COMPLETED", "REFUNDED", va h.k.
```

---

### refund

To'lovni qaytarish (partial mumkin).

```python
result = uzum.refund(
    order_id="uuid-order-id",
    amount=50000,  # Qisman qaytarish (tiyinda)
)
# result["operationId"]  →  operatsiya ID
```

---

### reverse (Checkout)

Avtorizatsiya qilingan to'lovni bekor qilish (TWO_STEP da, complete dan oldin).

```python
result = uzum.reverse(
    order_id="uuid-order-id",
    amount=150000,
)
```

---

### complete

Ikki bosqichli to'lovni tasdiqlash (TWO_STEP).

```python
result = uzum.complete(
    order_id="uuid-order-id",
    amount=150000,  # To'liq yoki qisman summa
)
```

---

### get_bindings

Saqlangan (tokenizatsiya qilingan) kartalar ro'yxati.

```python
result = uzum.get_bindings()
```

---

### get_receipts

Fiskal kvitansiyalarni olish.

```python
result = uzum.get_receipts(order_id="uuid-order-id")
```

---

## Tranzaksiya holatlari

### Merchant API (webhook)

```
CHECK (OK) → CREATE (PENDING) → CONFIRM (PAID)
                                       │
                                  REVERSE (CANCELED)
```

| Holat | Qiymat | Tavsif |
|-------|--------|--------|
| `PENDING` | `0` | Tranzaksiya yaratilgan, to'lov kutilmoqda |
| `PAID` | `1` | To'lov muvaffaqiyatli |
| `CANCELED` | `-1` | Bekor qilingan |

### Checkout API

| Status | Tavsif |
|--------|--------|
| `REGISTERED` | To'lov yaratilgan, hali to'lanmagan |
| `AUTHORIZED` | Mablag' hold qilingan (TWO_STEP) |
| `COMPLETED` | To'lov muvaffaqiyatli |
| `REFUNDED` | Qaytarilgan |
| `REVERSED` | Bekor qilingan |
| `DECLINED` | Rad etilgan |

---

## Xato kodlari

### Merchant API

| Kod | Tavsif |
|-----|--------|
| `10001` | Autentifikatsiya xatosi |
| `10002` | JSON parsing xatosi |
| `10003` | Noma'lum operatsiya |
| `10005` | So'rovda parametrlar yetarli emas |
| `10006` | Noto'g'ri serviceId |
| `10007` | To'lov allaqachon amalga oshirilgan |
| `10008` | Buyurtma topilmadi |
| `10009` | To'lov bekor qilingan |
| `99999` | Umumiy tekshiruv xatosi |

Barcha xato xabarlari 3 tilda (uz, ru, en) mavjud.

### Checkout API

| Kod | Tavsif |
|-----|--------|
| `0` | Muvaffaqiyatli |
| `1001` | Imzo tekshiruvi muvaffaqiyatsiz |
| `1002` | Token eskirgan yoki noto'g'ri |
| `1003` | Fingerprint mos emas |
| `2001` | Noto'g'ri parametrlar |
| `2002` | Majburiy maydon yo'q |
| `3000` | To'lov holati noto'g'ri |
| `3027` | Dublikat buyurtma raqami |
| `5000` | Ichki server xatosi |

---

## Xavfsizlik

### Xavfsizlik qatlamlari

| # | Qatlam | Tavsif |
|---|--------|--------|
| 1 | **IP whitelist** | `UZUM_ALLOWED_IPS` — faqat ruxsat etilgan IP'lardan webhook qabul qilinadi |
| 2 | **HTTP Basic Auth** | Har bir webhook so'rovda login:password tekshiriladi |
| 3 | **Service ID** | Har bir so'rovda `serviceId` validatsiya qilinadi |
| 4 | **Proxy IP aniqlash** | `X-Forwarded-For` orqali haqiqiy IP aniqlanadi |
| 5 | **Dublikat himoya** | Bir xil `transId` qayta yaratilmaydi (idempotent) |
| 6 | **Summa validatsiya** | `UZUM_ONE_TIME_PAYMENT=True` da modeldagi summa tekshiriladi |

### IP whitelist sozlash

`.env` da:
```env
UZUM_ALLOWED_IPS=1.2.3.4,5.6.7.8
```

Aniq IP manzillarni Uzum kabinetidan oling.

### Nginx bilan qo'shimcha himoya

```nginx
location /uzum/ {
    allow xxx.xxx.xxx.xxx;  # Uzum IP'larini Uzum kabinetidan oling
    deny all;
    proxy_pass http://127.0.0.1:8000;
}
```

### HTTPS

Uzum faqat HTTPS orqali ishlaydi. Server SSL sertifikatiga ega bo'lishi shart.

### Muhim qoidalar

- `UZUM_USERNAME`, `UZUM_PASSWORD`, `UZUM_API_KEY` ni hech qachon kodda hardcode qilmang
- `.env` faylni `.gitignore` ga qo'shing
- Production da `DEBUG=False` qo'ying

---

## Callback handler'lar

To'lov hodisalarini boshqarish uchun `UzumWebHookAPIView` ni override qiling:

```python
# yourapp/views.py
from uzum.views.base import BaseUzumWebHookAPIView


class MyUzumView(BaseUzumWebHookAPIView):

    def handle_check(self, params, result, *args, **kwargs):
        """CHECK chaqirilganda — buyurtma tekshiruvi."""
        order_id = params.get("order_id")
        # Qo'shimcha tekshiruvlar...

    def handle_created_payment(self, params, result, *args, **kwargs):
        """CREATE chaqirilganda — buyurtma "kutilmoqda" holatiga."""
        Order.objects.filter(pk=params.get("order_id")).update(status="pending")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        """CONFIRM chaqirilganda — buyurtma "to'langan" holatiga."""
        Order.objects.filter(pk=params.get("order_id")).update(status="paid")

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        """REVERSE chaqirilganda — buyurtma "bekor qilingan" holatiga."""
        Order.objects.filter(pk=params.get("order_id")).update(status="cancelled")
```

URL da:

```python
from django.urls import path
from yourapp.views import MyUzumView

urlpatterns = [
    path("uzum/<str:action>/", MyUzumView.as_view()),
]
```

---

## Deeplink yaratish

Uzum Bank ilovasi orqali to'lov uchun deeplink:

```python
from uzum import Uzum

link = Uzum.generate_pay_link(
    service_id=12345,
    order_id="order-42",
    amount=10000000,  # tiyinda
    redirect_url="https://example.com/success",
)
# Natija: https://www.uzumbank.uz/open-service?serviceId=12345&order_id=order-42&amount=10000000&redirectUrl=...
```

---

## Fiskal ma'lumotlar

### Checkout API da

`register_payment` da `cart` parametri orqali:

```python
cart = {
    "cartId": "unique-cart-id",
    "receiptType": "PURCHASE",    # yoki "PREPAID", "REFUND"
    "items": [
        {
            "title": "Mahsulot nomi",
            "productId": "prod-1",
            "quantity": 2,
            "unitPrice": 250000,       # birlik narxi (tiyinda)
            "total": 500000,           # jami (tiyinda)
            "spic": "12345678901234567",  # 17 belgili SPIC kodi
            "packageCode": "123456",
            "vatPercent": 12,          # QQS foizi
        }
    ]
}
```

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `cartId` | `str` | Savat ID (unikal) |
| `receiptType` | `str` | `PURCHASE`, `PREPAID`, yoki `REFUND` |
| `title` | `str` | Mahsulot nomi |
| `quantity` | `int` | Miqdori |
| `unitPrice` | `int` | Birlik narxi (tiyinda) |
| `total` | `int` | Jami summa (tiyinda) |
| `spic` | `str` | IKPU/SPIC kodi (17 belgi) |
| `packageCode` | `str` | Paket kodi |
| `vatPercent` | `int` | QQS foizi |

### Callback orqali kvitansiya

Fiskal chek tayyor bo'lganda Uzum callback yuboradi:

```json
{
    "orderId": "uuid",
    "receiptType": "PURCHASE",
    "receiptUrl": "https://..."
}
```

---

## Django Admin

`UzumTransactions` modeli admin panelda ko'rsatiladi:

- **Ko'rsatiladigan ustunlar:** ID, transId, orderId, summa, holat, sana
- **Filtrlar:** holat, sana
- **Qidiruv:** transId, orderId

O'chirish uchun: `UZUM_DISABLE_ADMIN=True`

---

## Ma'lumotlar bazasi

### `uzum_transactions` jadvali

| Ustun | Turi | Tavsif |
|-------|------|--------|
| `id` | `BigAutoField` | Asosiy kalit |
| `trans_id` | `CharField(255)` | Uzum tranzaksiya ID (unikal) |
| `order_id` | `CharField(256)` | Buyurtma ID |
| `amount` | `DecimalField(15,2)` | Summa (tiyinda) |
| `state` | `IntegerField` | 0=Pending, 1=Paid, -1=Canceled |
| `cancel_reason` | `CharField(255)` | Bekor qilish sababi |
| `created_at` | `DateTimeField` | Yaratilish vaqti |
| `updated_at` | `DateTimeField` | Yangilanish vaqti |
| `performed_at` | `DateTimeField` | To'lov vaqti |
| `cancelled_at` | `DateTimeField` | Bekor qilish vaqti |

---

## Amaliy misol

### 1. Order modeli

```python
# orders/models.py
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Yangi"),
        ("pending", "Kutilmoqda"),
        ("paid", "To'langan"),
        ("cancelled", "Bekor qilingan"),
    ]

    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
```

### 2. .env sozlash

```env
UZUM_USERNAME=my_login
UZUM_PASSWORD=my_password
UZUM_SERVICE_ID=12345
UZUM_ACCOUNT_MODEL=orders.models.Order
UZUM_ACCOUNT_FIELD=order_id
UZUM_AMOUNT_FIELD=amount
UZUM_ONE_TIME_PAYMENT=True
```

### 3. Webhook view

```python
# orders/views.py
from uzum.views.base import BaseUzumWebHookAPIView
from orders.models import Order

class OrderUzumView(BaseUzumWebHookAPIView):
    def handle_created_payment(self, params, result, *args, **kwargs):
        Order.objects.filter(pk=params.get("order_id")).update(status="pending")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        Order.objects.filter(pk=params.get("order_id")).update(status="paid")

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        Order.objects.filter(pk=params.get("order_id")).update(status="cancelled")
```

### 4. URL

```python
from django.urls import path
from orders.views import OrderUzumView

urlpatterns = [
    path("uzum/<str:action>/", OrderUzumView.as_view()),
]
```

### 5. Checkout orqali to'lov (karta)

```python
from uzum import Uzum

uzum = Uzum(
    terminal_id="your-terminal-uuid",
    api_key="your-api-key",
    is_test_mode=True,
)

# To'lov yaratish
result = uzum.register_payment(
    order_number=str(order.pk),
    amount=int(order.amount) * 100,  # so'mdan tiyinga
    return_url="https://example.com/success",
    callback_url="https://example.com/uzum/callback/",
)

# Foydalanuvchini to'lov sahifasiga yo'naltirish
redirect_url = result["paymentRedirectUrl"]
```

### 6. Deeplink (Uzum ilovasi orqali)

```python
link = Uzum.generate_pay_link(
    service_id=12345,
    order_id=str(order.pk),
    amount=int(order.amount) * 100,
    redirect_url="https://example.com/success",
)
```

### 7. Ishga tushirish

```bash
python manage.py makemigrations orders
python manage.py migrate
python manage.py runserver
```

Uzum kabinetida webhook URL sifatida `https://yourdomain.com/uzum/` ni ko'rsating.
