import typing as t
import uuid

from uzum.classes.http import UzumHttpClient
from uzum.const import Networks, PayType, ViewType


class Uzum:
    """
    Uzum Checkout API client.
    Karta orqali to'lov yaratish, holat tekshirish, refund va reverse.
    """

    def __init__(
        self,
        terminal_id: str,
        api_key: str,
        access_token: str = "",
        is_test_mode: bool = False,
    ) -> None:
        url = Networks.TEST_NET.value if is_test_mode else Networks.PROD_NET.value

        self.headers = {
            "Content-Type": "application/json",
            "X-Terminal-Id": terminal_id,
            "X-API-Key": api_key,
        }
        if access_token:
            self.headers["X-Merchant-Access-Token"] = access_token

        self.http = UzumHttpClient(base_url=url, headers=self.headers)

    def register_payment(
        self,
        order_number: str,
        amount: int,
        return_url: str,
        failure_url: str = "",
        callback_url: str = "",
        description: str = "",
        pay_type: str = PayType.ONE_STEP,
        view_type: str = ViewType.REDIRECT,
        session_timeout: int = 600,
        currency: int = 860,
        cart: t.Optional[dict] = None,
    ) -> dict:
        """
        To'lov yaratish. amount tiyinda.
        Qaytaradi: {"orderId": "...", "paymentRedirectUrl": "..."}
        """
        payload = {
            "viewType": view_type,
            "currency": currency,
            "orderNumber": order_number,
            "sessionTimeoutSecs": session_timeout,
            "amount": amount,
            "paymentParams": {"payType": pay_type},
            "returnUrl": return_url,
        }
        if failure_url:
            payload["failureUrl"] = failure_url
        if callback_url:
            payload["callbackUrl"] = callback_url
        if description:
            payload["description"] = description
        if cart:
            payload["cart"] = cart

        data = self.http.post("/api/v1/payment/register", payload)
        return data.get("result", {})

    def get_order_status(self, order_id: str) -> dict:
        """To'lov holatini tekshirish."""
        data = self.http.post("/api/v1/payment/getOrderStatus", {
            "orderId": order_id,
        })
        return data.get("result", {})

    def get_operation_state(self, operation_id: str) -> dict:
        """Operatsiya holatini tekshirish."""
        data = self.http.post("/api/v1/payment/getOperationState", {
            "operationId": operation_id,
        })
        return data.get("result", {})

    def get_receipts(self, order_id: str) -> dict:
        """Fiskal kvitansiyalarni olish."""
        data = self.http.post("/api/v1/payment/getReceipts", {
            "orderId": order_id,
        })
        return data.get("result", {})

    def refund(self, order_id: str, amount: int) -> dict:
        """
        To'lovni qaytarish (partial mumkin).
        amount tiyinda.
        """
        headers = {**self.headers, "X-Operation-Id": str(uuid.uuid4())}
        self.http.headers = headers
        data = self.http.post("/api/v1/acquiring/refund", {
            "orderId": order_id,
            "amount": amount,
        })
        self.http.headers = self.headers
        return data.get("result", {})

    def reverse(self, order_id: str, amount: int) -> dict:
        """To'lovni bekor qilish (authorize dan keyin, complete dan oldin)."""
        headers = {**self.headers, "X-Operation-Id": str(uuid.uuid4())}
        self.http.headers = headers
        data = self.http.post("/api/v1/acquiring/reverse", {
            "orderId": order_id,
            "amount": amount,
        })
        self.http.headers = self.headers
        return data.get("result", {})

    def complete(self, order_id: str, amount: int) -> dict:
        """Ikki bosqichli to'lovni tasdiqlash (TWO_STEP)."""
        headers = {**self.headers, "X-Operation-Id": str(uuid.uuid4())}
        self.http.headers = headers
        data = self.http.post("/api/v1/acquiring/complete", {
            "orderId": order_id,
            "amount": amount,
        })
        self.http.headers = self.headers
        return data.get("result", {})

    def get_bindings(self) -> dict:
        """Saqlangan kartalar ro'yxati."""
        data = self.http.post("/api/v1/acquiring/getBindings", {})
        return data.get("result", {})

    @staticmethod
    def generate_pay_link(
        service_id: int,
        order_id: str,
        amount: int,
        redirect_url: str = "",
    ) -> str:
        """
        Uzum Bank ilovasi orqali to'lov uchun deeplink.
        amount tiyinda.
        """
        url = f"https://www.uzumbank.uz/open-service?serviceId={service_id}"
        url += f"&order_id={order_id}&amount={amount}"
        if redirect_url:
            from urllib.parse import quote
            url += f"&redirectUrl={quote(redirect_url)}"
        return url
