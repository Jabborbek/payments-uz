# Payme Merchant API — To'liq Dokumentatsiya

## Mundarija

1. [Umumiy ma'lumot](#umumiy-malumot)
2. [O'rnatish](#ornatish)
3. [Sozlash (.env va settings.py)](#sozlash)
4. [Loyiha strukturasi](#loyiha-strukturasi)
5. [Merchant API metodlari](#merchant-api-metodlari)
   - [CheckPerformTransaction](#checkperformtransaction)
   - [CreateTransaction](#createtransaction)
   - [PerformTransaction](#performtransaction)
   - [CancelTransaction](#canceltransaction)
   - [CheckTransaction](#checktransaction)
   - [GetStatement](#getstatement)
   - [SetFiscalData](#setfiscaldata)
6. [Tranzaksiya holatlari](#tranzaksiya-holatlari)
7. [Bekor qilish sabablari](#bekor-qilish-sabablari)
8. [Xato kodlari](#xato-kodlari)
9. [Autentifikatsiya](#autentifikatsiya)
10. [Fiskal ma'lumotlar](#fiskal-malumotlar)
11. [To'lov havolasi yaratish](#tolov-havolasi-yaratish)
12. [Karta API](#karta-api)
13. [Kvitansiya (Receipt) API](#kvitansiya-api)
14. [Subscribe API (obuna to'lovlari)](#subscribe-api)
15. [Callback handler'lar](#callback-handlerlar)
16. [Django Admin](#django-admin)
17. [Ma'lumotlar bazasi](#malumotlar-bazasi)
18. [Test rejim](#test-rejim)
19. [Xavfsizlik](#xavfsizlik)

---

## Umumiy ma'lumot

Bu app [Payme Business](https://payme.uz) to'lov tizimi bilan integratsiya qilish uchun Django REST Framework asosida yozilgan to'liq yechim. App **JSON-RPC 2.0** protokolida ishlaydi va Payme'ning rasmiy [Merchant API dokumentatsiyasiga](https://developer.help.paycom.uz/protokol-merchant-api/) to'liq mos keladi.

**Qo'llab-quvvatlanadigan funksiyalar:**

- Merchant API webhook (7 ta metod)
- Karta boshqaruvi (yaratish, tasdiqlash, o'chirish)
- Kvitansiya/chek boshqaruvi
- Fiskal ma'lumotlar (OFD integratsiya)
- To'lov havolasi generatsiya qilish
- 12 soatlik tranzaksiya timeout
- 3 tilli xato xabarlari (uz, ru, en)

---

## O'rnatish

### 1. Kerakli paketlar

```bash
pip install django djangorestframework requests environs
```

### 2. Django settings.py ga qo'shish

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "payme",
]
```

### 3. URL sozlash

`config/urls.py` yoki loyihangizning root `urls.py` fayliga:

```python
from django.urls import path, include

urlpatterns = [
    path("payme/", include("payme.urls")),
]
```

Bu `POST /payme/update/` endpoint'ini yaratadi — Payme shu manzilga webhook so'rovlarini yuboradi.

### 4. Migratsiya

```bash
python manage.py migrate
```

Bu `payme_transactions` jadvalini yaratadi.

---

## Sozlash

### .env fayli

Loyiha root papkasida `.env` fayl yarating:

```env
# Django
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# ── Payme sozlamalari (MAJBURIY) ──────────────────

# Payme kabinetidan olinadigan merchant ID
PAYME_ID=5e730e8e0b852a417aa49ceb

# Payme kabinetidan olinadigan merchant API key
PAYME_KEY=ZPDODSiTYKuX0jyO8Gm1rKRMJOgMXMhy3YD6

# To'lov bog'lanadigan Django model (to'liq path)
PAYME_ACCOUNT_MODEL=orders.models.Order

# Account modelda to'lovni aniqlash uchun field nomi
PAYME_ACCOUNT_FIELD=order_id

# ── Payme sozlamalari (IXTIYORIY) ─────────────────

# One-time payment uchun summani tekshiradigan field
PAYME_AMOUNT_FIELD=amount

# True bo'lsa — summa account modeldagi qiymat bilan solishtiriladi
PAYME_ONE_TIME_PAYMENT=False

# True bo'lsa — test.paycom.uz ishlatiladi
PAYME_IS_TEST_MODE=True

# Fallback to'lov havolasi uchun ID
PAYME_FALLBACK_ID=

# True bo'lsa — Django admin'da PaymeTransactions ko'rinmaydi
PAYME_DISABLE_ADMIN=False

```

### settings.py dagi sozlamalar tavsifi

| Sozlama | Turi | Majburiy | Tavsif |
|---------|------|----------|--------|
| `PAYME_ID` | `str` | Ha | Payme kabinetidan olinadigan merchant ID |
| `PAYME_KEY` | `str` | Ha | Webhook autentifikatsiya uchun merchant key |
| `PAYME_ACCOUNT_MODEL` | `str` | Ha | To'lov bog'lanadigan model (`"app.models.Model"` formatda) |
| `PAYME_ACCOUNT_FIELD` | `str` | Ha | `account` parametridagi field nomi (masalan: `order_id`) |
| `PAYME_AMOUNT_FIELD` | `str` | Yo'q | One-time payment uchun summa field nomi (default: `amount`) |
| `PAYME_ONE_TIME_PAYMENT` | `bool` | Yo'q | `True` bo'lsa summani modeldagi qiymat bilan tekshiradi (default: `False`) |
| `PAYME_IS_TEST_MODE` | `bool` | Yo'q | `True` bo'lsa test server ishlatiladi (default: `False`) |
| `PAYME_FALLBACK_ID` | `str` | Yo'q | Fallback to'lov havolasi uchun ID |
| `PAYME_DISABLE_ADMIN` | `bool` | Yo'q | `True` bo'lsa admin panelda tranzaksiyalar ko'rinmaydi |

---

## Loyiha strukturasi

```
payments_package/
├── .env                              # Muhit o'zgaruvchilari
├── manage.py                         # Django CLI
├── config/
│   ├── __init__.py
│   ├── settings.py                   # Django sozlamalari
│   ├── urls.py                       # Root URL konfiguratsiya
│   └── wsgi.py                       # WSGI entry point
└── payme/
    ├── __init__.py                   # Payme client eksport
    ├── admin.py                      # Django admin registratsiya
    ├── apps.py                       # AppConfig
    ├── const.py                      # Network URL konstantalari
    ├── models.py                     # PaymeTransactions model
    ├── urls.py                       # Webhook endpoint
    ├── util.py                       # Vaqt konvertatsiya funksiyalari
    ├── classes/
    │   ├── cards.py                  # Karta API client
    │   ├── client.py                 # Asosiy Payme client (fasad)
    │   ├── http.py                   # HTTP so'rov yuboruvchi
    │   ├── initializer.py            # To'lov havolasi generator
    │   └── receipts.py               # Kvitansiya API client
    ├── exceptions/
    │   ├── general.py                # Karta va tarmoq xatoliklari
    │   └── webhook.py                # Merchant API xatoliklari
    ├── migrations/
    │   └── 0001_initial.py           # Boshlang'ich migratsiya
    ├── types/response/
    │   ├── cards.py                  # Karta javob tiplari
    │   ├── receipts.py               # Kvitansiya javob tiplari
    │   └── webhook.py                # Webhook javob tiplari
    └── views/
        ├── base.py                   # Asosiy webhook logic
        └── payme.py                  # Override qilinadigan view
```

---

## Merchant API metodlari

Barcha so'rovlar `POST /payme/update/` endpoint'iga JSON-RPC 2.0 formatida keladi. Barcha javoblar HTTP **200** qaytaradi (JSON-RPC standarti).

### So'rov formati

```json
{
    "method": "MethodName",
    "params": { ... },
    "id": 123
}
```

### Javob formati

**Muvaffaqiyatli:**
```json
{
    "result": { ... }
}
```

**Xato:**
```json
{
    "error": {
        "code": -31050,
        "message": {
            "uz": "Hisob topilmadi.",
            "ru": "Счет не найден.",
            "en": "Account does not exist."
        },
        "data": "Qo'shimcha ma'lumot"
    }
}
```

---

### CheckPerformTransaction

Tranzaksiya yaratishdan oldin to'lovni amalga oshirish mumkinligini tekshiradi.

**So'rov:**
```json
{
    "method": "CheckPerformTransaction",
    "params": {
        "amount": 500000,
        "account": {
            "order_id": "123"
        }
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `amount` | `int` | To'lov summasi **tiyinda** (1 so'm = 100 tiyin) |
| `account` | `object` | Foydalanuvchi identifikatori (`PAYME_ACCOUNT_FIELD` ga mos) |

**Javob:**
```json
{
    "result": {
        "allow": true
    }
}
```

**Fiskal ma'lumotlar bilan javob (ixtiyoriy):**
```json
{
    "result": {
        "allow": true,
        "additional": {
            "description": "Buyurtma #123"
        },
        "detail": {
            "receipt_type": 0,
            "shipping": {
                "title": "Yetkazib berish",
                "price": 500000
            },
            "items": [
                {
                    "discount": 0,
                    "title": "Mahsulot nomi",
                    "price": 500000,
                    "count": 1,
                    "code": "00702001001000001",
                    "units": 241092,
                    "vat_percent": 12,
                    "package_code": "123456"
                }
            ]
        }
    }
}
```

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31001` | Noto'g'ri summa |
| `-31050` | Hisob topilmadi |
| `-32400` | Tizim xatosi |

---

### CreateTransaction

Yangi tranzaksiya yaratadi. Tranzaksiya `INITIATING (1)` holatida saqlanadi.

**So'rov:**
```json
{
    "method": "CreateTransaction",
    "params": {
        "id": "53327b3fc92af52c0b72b695",
        "time": 1399114284039,
        "amount": 500000,
        "account": {
            "order_id": "123"
        }
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `id` | `string` | Payme tizimidagi tranzaksiya ID (MongoDB ObjectId) |
| `time` | `int` | Yaratilish vaqti (epoch dan millisekund) |
| `amount` | `int` | To'lov summasi tiyinda |
| `account` | `object` | Foydalanuvchi identifikatori |

**Javob:**
```json
{
    "result": {
        "transaction": "53327b3fc92af52c0b72b695",
        "state": 1,
        "create_time": 1399114284039,
        "receivers": null
    }
}
```

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `transaction` | `string` | Merchant tizimidagi tranzaksiya ID |
| `state` | `int` | Tranzaksiya holati (1 — yaratilgan) |
| `create_time` | `int` | Yaratilish vaqti (ms) |
| `receivers` | `null/array` | To'lov qabul qiluvchilar (ixtiyoriy) |

**Muhim qoidalar:**
- Bir xil `id` bilan qayta so'rov kelsa — mavjud tranzaksiya qaytariladi (idempotent)
- Tranzaksiya yaratilgandan keyin **12 soat** ichida `PerformTransaction` chaqirilmasa, avtomatik bekor bo'ladi (`state=-1`, `reason=4`)
- `PAYME_ONE_TIME_PAYMENT=True` bo'lsa, bitta account uchun faqat bitta faol tranzaksiya bo'lishi mumkin

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31001` | Noto'g'ri summa |
| `-31008` | Operatsiyani bajarib bo'lmaydi (timeout) |
| `-31050` | Hisob topilmadi |
| `-31099` | Tranzaksiya allaqachon mavjud |

---

### PerformTransaction

To'lovni yakunlaydi. Tranzaksiya `SUCCESSFULLY (2)` holatiga o'tadi.

**So'rov:**
```json
{
    "method": "PerformTransaction",
    "params": {
        "id": "53327b3fc92af52c0b72b695"
    }
}
```

**Javob:**
```json
{
    "result": {
        "transaction": "53327b3fc92af52c0b72b695",
        "state": 2,
        "perform_time": 1399114285002
    }
}
```

**Muhim qoidalar:**
- Allaqachon `perform` qilingan tranzaksiya uchun qayta so'rov kelsa — xuddi shu javob qaytariladi (idempotent)
- Bekor qilingan tranzaksiyani perform qilib bo'lmaydi (`-31008`)
- 12 soat o'tgan tranzaksiyani perform qilib bo'lmaydi — avtomatik bekor qilinadi (`reason=4`)

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31003` | Tranzaksiya topilmadi |
| `-31008` | Operatsiyani bajarib bo'lmaydi |

---

### CancelTransaction

Tranzaksiyani bekor qiladi. Yaratilgan va bajarilgan tranzaksiyalarni bekor qilish mumkin.

**So'rov:**
```json
{
    "method": "CancelTransaction",
    "params": {
        "id": "53327b3fc92af52c0b72b695",
        "reason": 2
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `id` | `string` | Payme tranzaksiya ID |
| `reason` | `int` | Bekor qilish sababi (1-5) |

**Javob:**
```json
{
    "result": {
        "transaction": "53327b3fc92af52c0b72b695",
        "state": -1,
        "cancel_time": 1399114286000
    }
}
```

| `state` | Ma'nosi |
|---------|---------|
| `-1` | Yaratilgan (state=1) tranzaksiya bekor qilindi |
| `-2` | Bajarilgan (state=2) tranzaksiya bekor qilindi |

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31003` | Tranzaksiya topilmadi |
| `-31007` | Buyurtma bajarilgan, bekor qilib bo'lmaydi |

---

### CheckTransaction

Tranzaksiya holatini so'raydi.

**So'rov:**
```json
{
    "method": "CheckTransaction",
    "params": {
        "id": "53327b3fc92af52c0b72b695"
    }
}
```

**Javob:**
```json
{
    "result": {
        "transaction": "53327b3fc92af52c0b72b695",
        "state": 2,
        "reason": null,
        "create_time": 1399114284039,
        "perform_time": 1399114285002,
        "cancel_time": 0
    }
}
```

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `state` | `int` | Joriy holat |
| `reason` | `int/null` | Bekor qilish sababi (agar bekor qilingan bo'lsa) |
| `create_time` | `int` | Yaratilish vaqti (ms) |
| `perform_time` | `int` | Bajarilish vaqti (ms, 0 agar bajarilmagan) |
| `cancel_time` | `int` | Bekor qilinish vaqti (ms, 0 agar bekor qilinmagan) |

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31003` | Tranzaksiya topilmadi |

---

### GetStatement

Belgilangan vaqt oralig'idagi tranzaksiyalar ro'yxatini qaytaradi. Solishtirma (reconciliation) uchun ishlatiladi.

**So'rov:**
```json
{
    "method": "GetStatement",
    "params": {
        "from": 1399114284039,
        "to": 1399120284000
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `from` | `int` | Boshlang'ich vaqt (ms) |
| `to` | `int` | Tugash vaqti (ms) |

**Javob:**
```json
{
    "result": {
        "transactions": [
            {
                "id": "53327b3fc92af52c0b72b695",
                "time": 1399114284039,
                "amount": 500000,
                "account": {
                    "order_id": "123"
                },
                "create_time": 1399114284039,
                "perform_time": 1399114285002,
                "cancel_time": 0,
                "transaction": "53327b3fc92af52c0b72b695",
                "state": 2,
                "reason": null,
                "receivers": null
            }
        ]
    }
}
```

**Muhim:**
- Faqat `CreateTransaction` orqali muvaffaqiyatli yaratilgan tranzaksiyalar qaytariladi
- `from <= time <= to` diapazondagi tranzaksiyalar (inklyuziv)
- Yaratilish vaqti bo'yicha **o'sish tartibida** (ascending) tartiblangan
- Bo'sh davr uchun bo'sh massiv qaytariladi

---

### SetFiscalData

Payme tomonidan fiskal kvitansiya ma'lumotlarini saqlash uchun chaqiriladi. Bu metod **Payme serveridan merchant serveriga** yuboriladi.

**So'rov:**
```json
{
    "method": "SetFiscalData",
    "params": {
        "id": "53327b3fc92af52c0b72b695",
        "type": "PERFORM",
        "fiscal_data": {
            "receipt_id": "123456",
            "status_code": 0,
            "message": "",
            "terminal_id": "UZ191234567890",
            "fiscal_sign": "123456789012",
            "qr_code_url": "https://ofd.uz/check?t=UZ191234567890&s=123456789012&r=123456&c=20230115120000",
            "date": "20230115120000"
        }
    }
}
```

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `id` | `string` | Payme tranzaksiya ID |
| `type` | `string` | `"PERFORM"` (to'lov) yoki `"CANCEL"` (qaytarish) |
| `fiscal_data` | `object` | Fiskal kvitansiya ma'lumotlari |

**`fiscal_data` obyekti:**

| Maydon | Turi | Tavsif |
|--------|------|--------|
| `receipt_id` | `string` | Virtual fiskal modul uchun ketma-ket to'lov raqami |
| `status_code` | `int` | Holat kodi |
| `message` | `string` | Xato tafsilotlari (agar ro'yxatdan o'tish muvaffaqiyatsiz bo'lsa) |
| `terminal_id` | `string` | Virtual fiskal modul identifikatori |
| `fiscal_sign` | `string` | Kvitansiyaning fiskal imzosi |
| `qr_code_url` | `string` | Fiskal kvitansiyaga havola |
| `date` | `string` | Soliq organida ro'yxatdan o'tish sanasi (YYYYMMDDHHMMSS) |

**Javob:**
```json
{
    "result": {
        "success": true
    }
}
```

**Muhim:**
- `PERFORM` va `CANCEL` uchun alohida fiskal kvitansiyalar yaratiladi
- App ularni `fiscal_data` JSON maydonida **alohida** saqlaydi:

```json
{
    "perform_data": { "receipt_id": "...", "terminal_id": "...", ... },
    "cancel_data": { "receipt_id": "...", "terminal_id": "...", ... }
}
```

**Mumkin bo'lgan xatolar:**

| Kod | Tavsif |
|-----|--------|
| `-31003` | Tranzaksiya topilmadi |
| `-32602` | Noto'g'ri fiskal parametrlar |

---

## Tranzaksiya holatlari

```
              CreateTransaction
                     │
                     ▼
    ┌─────────── INITIATING (1) ───────────┐
    │                │                      │
    │      PerformTransaction          CancelTransaction
    │                │                 yoki 12h timeout
    │                ▼                      │
    │        SUCCESSFULLY (2)               ▼
    │                │              CANCELED_DURING_INIT (-1)
    │        CancelTransaction
    │                │
    │                ▼
    │          CANCELED (-2)
    └───────────────────────────────────────┘
```

| Holat | Qiymat | Tavsif |
|-------|--------|--------|
| `INITIATING` | `1` | Tranzaksiya yaratilgan, to'lov kutilmoqda |
| `SUCCESSFULLY` | `2` | To'lov muvaffaqiyatli bajarilgan |
| `CANCELED_DURING_INIT` | `-1` | Yaratilgan tranzaksiya bekor qilindi |
| `CANCELED` | `-2` | Bajarilgan tranzaksiya bekor qilindi (refund) |

---

## Bekor qilish sabablari

| Sabab | Qiymat | Tavsif |
|-------|--------|--------|
| Payme tomonidan | `1` | Bir tomonlama: Payme (tashabbuskor) tomonidan bekor qilindi |
| Merchant tomonidan | `2` | Bir tomonlama: merchant (qabul qiluvchi) tomonidan bekor qilindi |
| Payme qaytarish | `3` | Muvaffaqiyatli to'lovdan keyin Payme tomonidan qaytarildi |
| Timeout | `4` | 12 soat ichida to'lanmagan tranzaksiya avtomatik bekor qilindi |
| Refund | `5` | Bajarilgan tranzaksiyani bekor qilish (qaytarish) |

---

## Xato kodlari

### Umumiy xatolar

| Kod | Tavsif |
|-----|--------|
| `-32300` | So'rov metodi POST emas |
| `-32700` | JSON parse xatosi |
| `-32600` | RPC so'rovda majburiy maydonlar yo'q yoki noto'g'ri |
| `-32601` | So'ralgan metod topilmadi |
| `-32504` | Autentifikatsiya xatosi (noto'g'ri merchant key) |
| `-32400` | Tizim/ichki xato |

### Metod-spetsifik xatolar

| Kod | Ishlatiladi | Tavsif |
|-----|-------------|--------|
| `-31001` | CheckPerform, Create | Noto'g'ri summa |
| `-31003` | Perform, Cancel, Check | Tranzaksiya topilmadi |
| `-31007` | Cancel | Buyurtma bajarilgan, bekor qilib bo'lmaydi |
| `-31008` | Create, Perform | Operatsiyani bajarib bo'lmaydi |
| `-31050` | CheckPerform, Create | Hisob topilmadi |
| `-31099` | Create | Tranzaksiya allaqachon mavjud |
| `-32602` | SetFiscalData | Noto'g'ri fiskal parametrlar |

### Xato javob formati

Barcha xato xabarlari 3 tilda qaytariladi:

```json
{
    "error": {
        "code": -31050,
        "message": {
            "uz": "Hisob topilmadi.",
            "ru": "Счет не найден.",
            "en": "Account does not exist."
        },
        "data": "Qo'shimcha tafsilot"
    }
}
```

---

## Autentifikatsiya

Payme **HTTP Basic Authentication** ishlatadi. Har bir so'rovda `Authorization` header yuboriladi:

```
Authorization: Basic base64(Paycom:{PAYME_KEY})
```

App bu headerni avtomatik tekshiradi. Noto'g'ri kalit bo'lsa `-32504` xato qaytariladi.

**Payme so'rovlari faqat quyidagi IP manzillardan keladi:**
`185.xxx.xxx.1` — `185.xxx.xxx.15` (aniq IP'larni Payme kabinetidan oling)

Xavfsizlik uchun server firewall'ida faqat shu IP'lardan so'rovlarni qabul qilish tavsiya etiladi.

---

## Fiskal ma'lumotlar

### Qanday ishlaydi

1. Payme to'lovni muvaffaqiyatli bajarganidan keyin (`PerformTransaction`) fiskal kvitansiya yaratadi
2. Payme `SetFiscalData` metodi orqali fiskal ma'lumotlarni merchant serveriga yuboradi
3. App bu ma'lumotlarni `PaymeTransactions.fiscal_data` JSON maydonida saqlaydi

### Saqlash formati

PERFORM va CANCEL ma'lumotlari **alohida** saqlanadi — biri ikkinchisining ustiga yozilmaydi:

```json
{
    "perform_data": {
        "receipt_id": "123456",
        "status_code": 0,
        "terminal_id": "UZ191234567890",
        "fiscal_sign": "123456789012",
        "qr_code_url": "https://ofd.uz/check?...",
        "date": "20230115120000"
    },
    "cancel_data": {
        "receipt_id": "789012",
        "status_code": 0,
        "terminal_id": "UZ191234567890",
        "fiscal_sign": "987654321098",
        "qr_code_url": "https://ofd.uz/check?...",
        "date": "20230116100000"
    }
}
```

### CheckPerformTransaction da fiskal detail

Fiskal kvitansiya uchun tovar tafsilotlarini `CheckPerformTransaction` javobida yuborish mumkin. Buning uchun `handle_pre_payment` callback'ini override qiling:

```python
from payme.views.base import BasePaymeWebHookAPIView
from payme.types.response.webhook import CheckPerformTransaction, Item


class MyPaymeView(BasePaymeWebHookAPIView):
    def handle_pre_payment(self, params, result, *args, **kwargs):
        order = Order.objects.get(pk=params["account"]["order_id"])

        # result ni o'zgartirish
        check = CheckPerformTransaction(allow=True, receipt_type=0)
        check.add_item(Item(
            discount=0,
            title=order.product_name,
            price=order.amount * 100,  # tiyinda
            count=1,
            code="00702001001000001",   # IKPU kodi
            units=241092,               # O'lchov birligi kodi
            vat_percent=12,             # QQS foizi
            package_code="123456",      # Paket kodi
        ))

        # result dict ni yangilash
        result.update(check.as_resp())
```

---

## To'lov havolasi yaratish

### Asosiy havola

```python
from payme import Payme

payme = Payme(
    payme_id="5e730e8e0b852a417aa49ceb",
    payme_key="your_key",
    is_test_mode=True,
)

# To'lov havolasi yaratish
link = payme.generate_pay_link(
    id=123,                                    # order_id
    amount=50000,                              # sumda (tiyin emas!)
    return_url="https://example.com/success",  # qaytish URL
)
# Natija: https://test.paycom.uz/{base64_encoded_params}
```

### Fallback havola

```python
link = payme.generate_fallback_link(
    form_fields={"amount": 50000, "order_id": 123}
)
# Natija: https://payme.uz/fallback/merchant/?id={fallback_id}&amount=50000&order_id=123
```

---

## Karta API

Karta operatsiyalari uchun `Payme` client ishlatiladi:

```python
from payme import Payme

payme = Payme(
    payme_id="your_id",
    is_test_mode=True,
)
```

### Karta yaratish

```python
response = payme.cards_create(
    number="8600495473316478",
    expire="0399",
    save=True,
)
token = response.result.card.token
```

### Tasdiqlash kodi so'rash

```python
response = payme.cards_get_verify_code(token=token)
# SMS yuboriladi: response.result.sent == True
```

### Kartani tasdiqlash

```python
response = payme.cards_verify(token=token, code="666666")
# response.result.card.verify == True
```

### Karta holatini tekshirish

```python
response = payme.cards_check(token=token)
```

### Kartani o'chirish

```python
response = payme.cards_remove(token=token)
# response.result.success == True
```

### Test

```python
payme.cards_test()  # Barcha karta operatsiyalarini test qiladi
```

**Test karta ma'lumotlari:**
- Raqam: `8600495473316478`
- Muddati: `0399`
- Tasdiqlash kodi: `666666`

---

## Kvitansiya API

Kvitansiya operatsiyalari uchun `payme_key` ham kerak:

```python
payme = Payme(
    payme_id="your_id",
    payme_key="your_key",
    is_test_mode=True,
)
```

### Kvitansiya yaratish

```python
response = payme.receipts_create(
    account={"order_id": 123},
    amount=500000,  # tiyinda
    description="Buyurtma #123 uchun to'lov",
    detail={"items": [...]},
)
receipt_id = response.result.receipt._id
```

### Kvitansiyani to'lash

```python
response = payme.receipts_pay(
    receipts_id=receipt_id,
    token=card_token,
)
# response.result.receipt.state == 4  (to'langan)
```

### Kvitansiyani SMS orqali yuborish

```python
response = payme.receipts_send(
    receipts_id=receipt_id,
    phone="998901234567",
)
```

### Kvitansiyani bekor qilish

```python
response = payme.receipts_cancel(receipts_id=receipt_id)
```

### Kvitansiya holatini tekshirish

```python
response = payme.receipts_check(receipts_id=receipt_id)
```

### Kvitansiya tafsilotlarini olish

```python
response = payme.receipts_get(receipts_id=receipt_id)
```

### Barcha kvitansiyalarni olish

```python
response = payme.receipts_get_all(
    count=10,
    from_=1730322122000,
    to=1730398982000,
    offset=0,
)
```

### Fiskal ma'lumot qo'shish

```python
response = payme.receipts_set_fiscal_data(
    receipt_id=receipt_id,
    qr_code_url="https://ofd.uz/check?t=UZ123&s=456&r=789&c=20230115",
)
```

---

## Callback handler'lar

To'lov hodisalarini boshqarish uchun `PaymeWebHookAPIView` ni override qiling:

```python
# yourapp/views.py
from payme.views.base import BasePaymeWebHookAPIView


class MyPaymeWebHookView(BasePaymeWebHookAPIView):

    def handle_pre_payment(self, params, result, *args, **kwargs):
        """
        CheckPerformTransaction chaqirilganda ishlaydi.
        To'lovdan oldingi tekshiruvlar uchun.
        """
        order_id = params["account"]["order_id"]
        # Buyurtma mavjudligini, holatini tekshirish...

    def handle_created_payment(self, params, result, *args, **kwargs):
        """
        CreateTransaction chaqirilganda ishlaydi.
        Buyurtma holatini "to'lov kutilmoqda" ga o'zgartirish uchun.
        """
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="pending")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        """
        PerformTransaction chaqirilganda ishlaydi.
        Buyurtma holatini "to'langan" ga o'zgartirish uchun.
        """
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="paid")

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        """
        CancelTransaction chaqirilganda ishlaydi.
        Buyurtmani bekor qilish uchun.
        """
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="cancelled")
```

Keyin `urls.py` da:

```python
from django.urls import path
from yourapp.views import MyPaymeWebHookView

urlpatterns = [
    path("payme/update/", MyPaymeWebHookView.as_view()),
]
```

---

## Django Admin

`PaymeTransactions` modeli avtomatik ravishda Django admin panelida ro'yxatdan o'tkaziladi.

**Admin interfeys ko'rsatadi:**
- Tranzaksiya ID
- Holat (state)
- Bekor qilish sababi
- Yaratilish sanasi

**Filtrlar:** holat, bekor qilish sababi, sana
**Qidiruv:** tranzaksiya ID, hisob ID

Admin panelni o'chirish uchun `.env` ga `PAYME_DISABLE_ADMIN=True` qo'shing.

---

## Ma'lumotlar bazasi

### `payme_transactions` jadvali

| Ustun | Turi | Tavsif |
|-------|------|--------|
| `id` | `BigAutoField` | Asosiy kalit |
| `transaction_id` | `CharField(50)` | Payme tranzaksiya ID |
| `account_id` | `CharField(256)` | Foydalanuvchi/buyurtma ID |
| `amount` | `DecimalField(15,2)` | To'lov summasi |
| `state` | `IntegerField` | Tranzaksiya holati (1, 2, -1, -2) |
| `fiscal_data` | `JSONField` | Fiskal kvitansiya ma'lumotlari |
| `cancel_reason` | `IntegerField` | Bekor qilish sababi (1-5) |
| `created_at` | `DateTimeField` | Yaratilish vaqti (indekslangan) |
| `updated_at` | `DateTimeField` | Yangilanish vaqti (indekslangan) |
| `performed_at` | `DateTimeField` | Bajarilish vaqti (indekslangan) |
| `cancelled_at` | `DateTimeField` | Bekor qilinish vaqti (indekslangan) |

---

## Test rejim

### Yoqish

`.env` da:
```env
PAYME_IS_TEST_MODE=True
```

### Farqlari

| | Production | Test |
|---|---|---|
| API URL | `https://checkout.paycom.uz/api` | `https://checkout.test.paycom.uz/api` |
| To'lov URL | `https://checkout.paycom.uz/` | `https://test.paycom.uz/` |
| Pul yechiladi | Ha | Yo'q |

### Test karta

| Maydon | Qiymat |
|--------|--------|
| Karta raqami | `8600495473316478` |
| Amal qilish muddati | `03/99` |
| SMS tasdiqlash kodi | `666666` |

---

## Xavfsizlik

### Tavsiyalar

1. **IP cheklash** — Payme faqat `185.xxx.xxx.1` — `185.xxx.xxx.15` (aniq IP'larni Payme kabinetidan oling) IP'lardan so'rov yuboradi. Firewall'da faqat shu IP'larga ruxsat bering:

```nginx
# Nginx konfiguratsiya
location /payme/update/ {
    allow xxx.xxx.xxx.0/28;  # Aniq IP ni Payme kabinetidan oling
    deny all;
    proxy_pass http://127.0.0.1:8000;
}
```

2. **HTTPS** — Payme faqat TLS v1/v1.1/v1.2 orqali ishlaydi. Server HTTPS bo'lishi shart.

3. **SECRET_KEY** — `.env` da saqlang, git'ga qo'shmang:

```gitignore
.env
db.sqlite3
```

4. **PAYME_KEY** — Payme kabinetidan oling, hech qachon kodda hardcode qilmang.

5. **DEBUG** — Productionda `DEBUG=False` qo'ying.

---

## Subscribe API

Subscribe API — bu **obuna/qayta-qayta to'lovlar** uchun mo'ljallangan alohida protokol. Merchant API dan farqli ravishda, bu yerda **merchant Payme'ga** so'rov yuboradi (teskari yo'nalish).

### Merchant API vs Subscribe API

| Jihat | Merchant API | Subscribe API |
|-------|-------------|---------------|
| **Yo'nalish** | Payme → Merchant | Merchant → Payme |
| **Foydalanish** | Bir martalik to'lov (checkout) | Obuna/qayta-qayta to'lov |
| **Karta** | Payme o'zi boshqaradi | Merchant tokenlashtiradi |
| **Nazorat** | Payme boshqaradi | Merchant boshqaradi |
| **Metodlar** | CheckPerform, Create, Perform... | cards.\*, receipts.\* |
| **Autentifikatsiya** | Payme merchant key bilan keladi | Merchant `X-Auth` header yuboradi |

### Endpoint'lar

| Muhit | URL |
|-------|-----|
| Test | `https://checkout.test.paycom.uz/api` |
| Production | `https://checkout.paycom.uz/api` |

### Autentifikatsiya

`X-Auth` header ikki xil formatda ishlatiladi:

- **Frontend (client-side):** `X-Auth: {payme_id}` — faqat merchant ID
- **Backend (server-side):** `X-Auth: {payme_id}:{payme_key}` — merchant ID + key

### To'liq obuna to'lov oqimi

```
1. cards.create (save=true)      ← Karta tokenlashtirish (client)
         │
2. cards.get_verify_code          ← SMS kod so'rash (client)
         │
3. cards.verify                   ← SMS kod tasdiqlash (client)
         │
    ┌────┴────┐
    │  TOKEN  │  ← Saqlab qo'yiladi (DB yoki xotira)
    └────┬────┘
         │
   ╔═════╧══════════════════════╗
   ║  Har oylik/haftalik to'lov ║  ← Takrorlanadigan qism
   ╠════════════════════════════╣
   ║ 4. receipts.create         ║  ← Kvitansiya yaratish (server)
   ║         │                  ║
   ║ 5. receipts.pay (token)    ║  ← Token bilan to'lash (server)
   ╚════════════════════════════╝
         │
6. cards.remove                   ← Obunani bekor qilish (server)
```

**Muhim:** 1-3 qadamlar faqat bir marta. 4-5 qadamlar har safar to'lov kerak bo'lganda takrorlanadi — kartani qayta kiritish yoki tasdiqlash shart emas.

### Kod misoli: to'liq obuna integratsiya

#### 1-qadam: Payme client yaratish

```python
from payme import Payme

payme = Payme(
    payme_id="your_merchant_id",
    payme_key="your_merchant_key",
    is_test_mode=True,
)
```

#### 2-qadam: Karta tokenlashtirish (bir martalik)

```python
# Foydalanuvchi karta ma'lumotlarini kiritadi
card_response = payme.cards_create(
    number="8600495473316478",
    expire="0399",
    save=True,  # MUHIM: True = qayta-qayta to'lov uchun
)
token = card_response.result.card.token

# SMS tasdiqlash kodi so'rash
payme.cards_get_verify_code(token=token)

# Foydalanuvchi SMS kodni kiritadi
verify_response = payme.cards_verify(token=token, code="666666")
token = verify_response.result.card.token  # Token yangilanishi mumkin!

# Tokenni DB ga saqlash (masalan: UserCard modeliga)
user.card_token = token
user.save()
```

#### 3-qadam: Obuna to'lovi (har oy takrorlanadi)

```python
# Kvitansiya yaratish
receipt = payme.receipts_create(
    account={"order_id": str(subscription.pk)},
    amount=100000,  # 1000 so'm (tiyinda)
    description="Oylik obuna to'lovi",
)
receipt_id = receipt.result.receipt._id

# Saqlangan token bilan to'lash
pay_response = payme.receipts_pay(
    receipts_id=receipt_id,
    token=user.card_token,
)
# pay_response.result.receipt.state == 4  →  to'langan
```

#### 4-qadam: Obunani bekor qilish

```python
# Saqlangan tokenni o'chirish
payme.cards_remove(token=user.card_token)

user.card_token = None
user.save()
```

### Subscribe API metodlari

#### cards.create

Kartani tokenlashtiradi. `save=True` bo'lsa token qayta ishlatiladi, `save=False` bo'lsa bir martalik.

```python
response = payme.cards_create(
    number="8600495473316478",
    expire="0399",
    save=True,
)
# response.result.card.token    — token
# response.result.card.verify   — False (hali tasdiqlanmagan)
# response.result.card.recurrent — True (qayta to'lov uchun yaroqli)
```

#### cards.get_verify_code

Karta egasining telefoniga SMS OTP yuboradi.

```python
response = payme.cards_get_verify_code(token=token)
# response.result.sent  — True (SMS yuborildi)
# response.result.phone — "99890*****31" (yashirilgan raqam)
# response.result.wait  — 60000 (OTP amal qilish muddati, ms)
```

#### cards.verify

SMS kodni tekshiradi. Muvaffaqiyatli bo'lsa karta tasdiqlangan hisoblanadi.

```python
response = payme.cards_verify(token=token, code="666666")
# response.result.card.verify — True (tasdiqlangan)
# DIQQAT: token qiymati o'zgarishi mumkin!
new_token = response.result.card.token
```

#### cards.check

Token hali yaroqli ekanligini tekshiradi.

```python
response = payme.cards_check(token=token)
# response.result.card.verify    — True/False
# response.result.card.recurrent — True/False
```

#### cards.remove

Saqlangan tokenni o'chiradi. Obunani bekor qilishda ishlatiladi.

```python
response = payme.cards_remove(token=token)
# response.result.success — True
```

#### receipts.create

To'lov kvitansiyasi yaratadi.

```python
response = payme.receipts_create(
    account={"order_id": "123"},
    amount=500000,  # tiyinda
    description="Obuna to'lovi",
    detail={                              # Fiskal ma'lumotlar (ixtiyoriy)
        "receipt_type": 0,
        "items": [{
            "title": "Oylik obuna",
            "price": 500000,
            "count": 1,
            "code": "00702001001000001",   # IKPU kodi
            "units": 241092,
            "vat_percent": 12,
            "package_code": "123456",
        }]
    },
)
receipt_id = response.result.receipt._id
```

#### receipts.pay

Kvitansiyani karta tokeni bilan to'laydi.

```python
response = payme.receipts_pay(
    receipts_id=receipt_id,
    token=card_token,
)
# response.result.receipt.state == 4  →  muvaffaqiyatli
```

#### receipts.send

Kvitansiyani SMS orqali foydalanuvchiga yuboradi.

```python
response = payme.receipts_send(
    receipts_id=receipt_id,
    phone="998901234567",
)
# response.result.success — True
```

#### receipts.cancel

To'langan kvitansiyani bekor qiladi (refund).

```python
response = payme.receipts_cancel(receipts_id=receipt_id)
# response.result.receipt.state == 21  →  bekor qilishga navbatda
```

#### receipts.check

Kvitansiya holatini tekshiradi.

```python
response = payme.receipts_check(receipts_id=receipt_id)
# response.result.state — 4 (to'langan), 50 (bekor qilingan), va h.k.
```

#### receipts.get

Kvitansiya tafsilotlarini oladi.

```python
response = payme.receipts_get(receipts_id=receipt_id)
```

#### receipts.get_all

Vaqt oralig'idagi barcha kvitansiyalarni oladi.

```python
response = payme.receipts_get_all(
    count=50,         # Eng ko'pi bilan 50
    from_=1730322122000,
    to=1730398982000,
    offset=0,
)
```

#### receipts.set_fiscal_data

Fiskal QR kod URL orqali fiskal ma'lumotlarni bog'laydi.

```python
response = payme.receipts_set_fiscal_data(
    receipt_id=receipt_id,
    qr_code_url="https://ofd.uz/check?t=UZ123&s=456&r=789&c=20230115120000",
)
```

### Xavfsizlik talablari (Subscribe API)

- Karta ma'lumotlarini **hech qachon** merchant serverida saqlamang — faqat token saqlang
- Frontend formada `name` atributi bo'lmasligi kerak (karta ma'lumotlari serverga yuborilmasligi uchun)
- Form tagida `action` atributi bo'lmasligi kerak
- Payme logotipi va foydalanish shartlariga havola ko'rsatilishi shart

---

## Amaliy misol: to'liq integratsiya

### 1. Order modeli yaratish

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Yangi"),
        ("pending", "To'lov kutilmoqda"),
        ("paid", "To'langan"),
        ("cancelled", "Bekor qilingan"),
    ]

    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. .env sozlash

```env
PAYME_ACCOUNT_MODEL=orders.models.Order
PAYME_ACCOUNT_FIELD=order_id
PAYME_AMOUNT_FIELD=amount
PAYME_ONE_TIME_PAYMENT=True
```

### 3. Webhook view yaratish

```python
# orders/views.py
from payme.views.base import BasePaymeWebHookAPIView
from orders.models import Order


class OrderPaymeView(BasePaymeWebHookAPIView):
    def handle_created_payment(self, params, result, *args, **kwargs):
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="pending")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="paid")

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        order_id = params["account"]["order_id"]
        Order.objects.filter(pk=order_id).update(status="cancelled")
```

### 4. URL sozlash

```python
# config/urls.py
from django.urls import path
from orders.views import OrderPaymeView

urlpatterns = [
    path("payme/update/", OrderPaymeView.as_view()),
]
```

### 5. To'lov havolasi yaratish

```python
from payme import Payme

payme = Payme(payme_id="your_id", is_test_mode=True)

link = payme.generate_pay_link(
    id=order.pk,
    amount=int(order.amount),
    return_url="https://example.com/orders/success/",
)
# Bu havolani foydalanuvchiga yuboring
```

### 6. Migratsiya va ishga tushirish

```bash
python manage.py makemigrations orders
python manage.py migrate
python manage.py runserver
```

Payme kabinetida webhook URL sifatida `https://yourdomain.com/payme/update/` ni ko'rsating.
