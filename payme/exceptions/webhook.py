import logging
import typing as t

from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

MessageT = t.Optional[t.Union[str, t.Dict[str, str]]]


class BasePaymeException(APIException):
    status_code: int = status.HTTP_200_OK
    error_code: t.Optional[int] = None
    message: MessageT = None

    def __init__(self, message: str = None):
        detail: dict = {
            "error": {"code": self.error_code, "message": self.message, "data": message}
        }
        logger.error(f"Payme error detail: {detail}")
        self.detail = detail


class PermissionDenied(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -32504
    message = {
        "uz": "Ruxsat berilmagan.",
        "ru": "Недостаточно привилегий для выполнения метода.",
        "en": "Permission denied.",
    }


class InternalServiceError(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -32400
    message = {
        "uz": "Tizimda xatolik yuzaga keldi.",
        "ru": "Внутренняя ошибка сервиса.",
        "en": "Internal service error.",
    }


class MethodNotFound(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -32601
    message = {
        "uz": "So'ralgan metod topilmadi.",
        "ru": "Запрашиваемый метод не найден.",
        "en": "Method not found.",
    }


class AccountDoesNotExist(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31050
    message = {
        "uz": "Hisob topilmadi.",
        "ru": "Счет не найден.",
        "en": "Account does not exist.",
    }


class IncorrectAmount(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31001
    message = {
        "ru": "Неверная сумма.",
        "uz": "Noto'g'ri summa.",
        "en": "Incorrect amount.",
    }


class TransactionAlreadyExists(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31099
    message = {
        "uz": "Tranzaksiya allaqachon mavjud.",
        "ru": "Транзакция уже существует.",
        "en": "Transaction already exists.",
    }


class InvalidFiscalParams(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -32602
    message = {
        "uz": "Fiskal parameterlarida kamchiliklar bor.",
        "ru": "Неверные фискальные параметры.",
        "en": "Invalid fiscal parameters.",
    }


class InvalidAccount(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -32400
    message = {
        "uz": "Hisob nomida kamchilik bor.",
        "ru": "Неверный номер счета.",
        "en": "Invalid account.",
    }


class TransactionNotFound(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31003
    message = {
        "uz": "Tranzaksiya topilmadi.",
        "ru": "Транзакция не найдена.",
        "en": "Transaction not found.",
    }


class UnableToCancelTransaction(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31007
    message = {
        "uz": "Buyurtma bajarilgan, tranzaksiyani bekor qilib bo'lmaydi.",
        "ru": "Заказ выполнен. Невозможно отменить транзакцию.",
        "en": "Order completed. Unable to cancel transaction.",
    }


class UnableToPerformOperation(BasePaymeException):
    status_code = status.HTTP_200_OK
    error_code = -31008
    message = {
        "uz": "Operatsiyani bajarib bo'lmaydi.",
        "ru": "Невозможно выполнить операцию.",
        "en": "Unable to perform operation.",
    }


exception_whitelist = (
    IncorrectAmount,
    MethodNotFound,
    PermissionDenied,
    AccountDoesNotExist,
    TransactionAlreadyExists,
    InvalidFiscalParams,
    InvalidAccount,
    TransactionNotFound,
    UnableToCancelTransaction,
    UnableToPerformOperation,
)
