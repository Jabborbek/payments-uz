from enum import Enum


class Networks(str, Enum):
    PROD_NET = "https://checkout-api.ipt-merch.com"
    TEST_NET = "https://checkout-api.ipt-merch.com"


class PaymentStatus(str, Enum):
    REGISTERED = "REGISTERED"
    AUTHORIZED = "AUTHORIZED"
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"
    REVERSED = "REVERSED"
    DECLINED = "DECLINED"


class MerchantStatus(str, Enum):
    OK = "OK"
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    REVERSED = "REVERSED"
    FAILED = "FAILED"


class PayType(str, Enum):
    ONE_STEP = "ONE_STEP"
    TWO_STEP = "TWO_STEP"


class ViewType(str, Enum):
    REDIRECT = "REDIRECT"
    WEB_VIEW = "WEB_VIEW"
    IFRAME = "IFRAME"
