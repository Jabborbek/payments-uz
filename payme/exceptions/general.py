import logging


class BaseError(Exception):
    logger = logging.getLogger(__name__)

    def __init__(self, code, message, data=None):
        super().__init__(message)
        self.code = code
        self.data = data
        self.logger.error(f"Error {code}: {message}. Data: {data}")


class CardError(BaseError):
    pass


class TransportError(CardError):
    message = "Transport error."

    def __init__(self, data=None):
        super().__init__(-32300, self.message, data)


class ParseError(CardError):
    message = "Parse error."

    def __init__(self, data=None):
        super().__init__(-32700, self.message, data)


class InvalidRequestError(CardError):
    message = "Invalid Request."

    def __init__(self, data=None):
        super().__init__(-32600, self.message, data)


class InvalidResponseError(CardError):
    message = "Invalid Response."

    def __init__(self, data=None):
        super().__init__(-32600, self.message, data)


class SystemError(CardError):
    message = "System error."

    def __init__(self, data=None):
        super().__init__(-32400, self.message, data)


class MethodNotFoundError(CardError):
    message = "Method not found."

    def __init__(self, data=None):
        super().__init__(-32601, self.message, data)


class InvalidParamsError(CardError):
    message = "Invalid Params."

    def __init__(self, data=None):
        super().__init__(-32602, self.message, data)


class InvalidTokenFormat(CardError):
    message = "Invalid token format."

    def __init__(self, data=None):
        super().__init__(-32500, self.message, data)


class AccessDeniedError(CardError):
    message = "Access denied."

    def __init__(self, data=None):
        super().__init__(-32504, self.message, data)


class CardNotFoundError(CardError):
    message = "Card not found."

    def __init__(self, data=None):
        super().__init__(-31400, self.message, data)


class SmsNotConnectedError(CardError):
    message = "SMS notification not connected."

    def __init__(self, data=None):
        super().__init__(-31301, self.message, data)


class CardExpiredError(CardError):
    message = "Card has expired."

    def __init__(self, data=None):
        super().__init__(-31301, self.message, data)


class CardBlockedError(CardError):
    message = "Card is blocked."

    def __init__(self, data=None):
        super().__init__(-31301, self.message, data)


class CorporateCardError(CardError):
    message = "Financial operations with corporate cards are not allowed."

    def __init__(self, data=None):
        super().__init__(-31300, self.message, data)


class BalanceError(CardError):
    message = "Unable to retrieve card balance. Please try again later."

    def __init__(self, data=None):
        super().__init__(-31302, self.message, data)


class InsufficientFundsError(CardError):
    message = "Insufficient funds on the card."

    def __init__(self, data=None):
        super().__init__(-31303, self.message, data)


class InsufficientFundsErrorV2(CardError):
    message = "Insufficient funds on the card."

    def __init__(self, data=None):
        super().__init__(-31630, self.message, data)


class InvalidCardNumberError(CardError):
    message = "Invalid card number."

    def __init__(self, data=None):
        super().__init__(-31300, self.message, data)


class CardNotFoundWithNumberError(CardError):
    message = "Card with this number not found."

    def __init__(self, data=None):
        super().__init__(-31300, self.message, data)


class InvalidExpiryDateError(CardError):
    message = "Invalid expiry date for the card."

    def __init__(self, data=None):
        super().__init__(-31300, self.message, data)


class ProcessingServerError(CardError):
    message = "Processing center server is unavailable. Please try again later."

    def __init__(self, data=None):
        super().__init__(-31002, self.message, data)


class OtpError(BaseError):
    pass


class OtpSendError(OtpError):
    message = "Error occurred while sending SMS. Please try again."

    def __init__(self, data=None):
        super().__init__(-31110, self.message, data)


class OtpCheckError(OtpError):
    pass


class OtpExpiredError(OtpCheckError):
    message = "OTP code has expired. Request a new code."

    def __init__(self, data=None):
        super().__init__(-31101, self.message, data)


class OtpAttemptsExceededError(OtpCheckError):
    message = "Number of attempts to enter the code has been exceeded."

    def __init__(self, data=None):
        super().__init__(-31102, self.message, data)


class OtpInvalidCodeError(OtpCheckError):
    message = "Invalid OTP code."

    def __init__(self, data=None):
        super().__init__(-31103, self.message, data)


class PaymeNetworkError(BaseError):
    message = "Network error occurred during request to Payme server."

    def __init__(self, data=None):
        super().__init__(self.message, data)


class ReceiptsNotFoundError(BaseException):
    def __init__(self, message="No receipts found for the given transaction ID.", data=None):
        super().__init__(message, data)


errors_map = {
    -32300: TransportError,
    -32700: ParseError,
    -32600: InvalidRequestError,
    -32601: MethodNotFoundError,
    -32602: InvalidParamsError,
    -32504: AccessDeniedError,
    -31400: CardNotFoundError,
    -31301: SmsNotConnectedError,
    -31302: BalanceError,
    -31303: InsufficientFundsError,
    -31630: InsufficientFundsErrorV2,
    -31300: InvalidCardNumberError,
    -31002: ProcessingServerError,
    -31110: OtpSendError,
    -31101: OtpExpiredError,
    -31102: OtpAttemptsExceededError,
    -31103: OtpInvalidCodeError,
    -31602: ReceiptsNotFoundError,
    -32500: InvalidTokenFormat,
    -32400: SystemError
}
