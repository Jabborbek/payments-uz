import logging

logger = logging.getLogger(__name__)


class UzumError:
    """Mixin for Uzum error codes — not an exception, used in responses."""

    # Merchant API error codes
    AUTH_ERROR = 10001
    PARSE_ERROR = 10002
    UNKNOWN_OPERATION = 10003
    NOT_ENOUGH_PARAMS = 10005
    INVALID_SERVICE_ID = 10006
    ALREADY_PROCESSED = 10007
    ORDER_NOT_FOUND = 10008
    PAYMENT_CANCELLED = 10009
    VALIDATION_ERROR = 99999

    MESSAGES = {
        10001: {
            "uz": "Autentifikatsiya xatosi.",
            "ru": "Ошибка авторизации.",
            "en": "Authorization error.",
        },
        10002: {
            "uz": "JSON formatida xatolik.",
            "ru": "Ошибка парсинга JSON.",
            "en": "JSON parsing error.",
        },
        10003: {
            "uz": "Noma'lum operatsiya.",
            "ru": "Неизвестная операция.",
            "en": "Unknown operation.",
        },
        10005: {
            "uz": "So'rovda yetarli parametrlar yo'q.",
            "ru": "Недостаточно параметров в запросе.",
            "en": "Not enough parameters in request.",
        },
        10006: {
            "uz": "Noto'g'ri serviceId.",
            "ru": "Неверный serviceId.",
            "en": "Invalid service ID.",
        },
        10007: {
            "uz": "To'lov allaqachon amalga oshirilgan.",
            "ru": "Платёж уже обработан.",
            "en": "Payment already processed.",
        },
        10008: {
            "uz": "Buyurtma topilmadi.",
            "ru": "Заказ не найден.",
            "en": "Order not found.",
        },
        10009: {
            "uz": "To'lov bekor qilingan.",
            "ru": "Платёж отменён.",
            "en": "Payment cancelled.",
        },
        99999: {
            "uz": "To'lov ma'lumotlarini tekshirishda xatolik.",
            "ru": "Ошибка проверки данных платежа.",
            "en": "Error checking payment data.",
        },
    }

    @classmethod
    def get_message(cls, code: int) -> dict:
        return cls.MESSAGES.get(code, cls.MESSAGES[99999])
