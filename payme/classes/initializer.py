import base64

from django.conf import settings


class Initializer:
    def __init__(
        self, payme_id: str = None, fallback_id: str = None, is_test_mode: bool = False
    ) -> None:
        self.payme_id = payme_id
        self.fallback_id = fallback_id
        self.is_test_mode = is_test_mode

    def generate_pay_link(self, id: int, amount: int, return_url: str) -> str:
        amount = amount * 100
        params = f"m={self.payme_id};ac.{settings.PAYME_ACCOUNT_FIELD}={id};a={amount};c={return_url}"
        params = base64.b64encode(params.encode("utf-8")).decode("utf-8")

        if self.is_test_mode is True:
            return f"https://test.paycom.uz/{params}"

        return f"https://checkout.paycom.uz/{params}"

    def generate_fallback_link(self, form_fields: dict | None = None):
        result = f"https://payme.uz/fallback/merchant/?id={self.fallback_id}"

        if form_fields is not None:
            for key, value in form_fields.items():
                result += f"&{key}={value}"

        return result
