import typing as t

from payme.const import Networks

from payme.classes.cards import Cards
from payme.classes.receipts import Receipts
from payme.classes.initializer import Initializer
from payme.types.response import cards as card_response
from payme.types.response import receipts as receipt_response


class Payme:
    def __init__(
        self,
        payme_id: str,
        payme_key: t.Optional[str] = None,
        is_test_mode: bool = False,
        fallback_id: t.Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        url = Networks.PROD_NET.value

        if is_test_mode is True:
            url = Networks.TEST_NET.value

        self.cards = Cards(url=url, payme_id=payme_id)
        self.initializer = Initializer(
            payme_id=payme_id, fallback_id=fallback_id, is_test_mode=is_test_mode
        )
        if payme_key:
            self.receipts = Receipts(url=url, payme_id=payme_id, payme_key=payme_key)

    def cards_create(
        self, number: str, expire: str, save: bool = False, timeout: int = 10
    ) -> card_response.CardsCreateResponse:
        return self.cards.create(number=number, expire=expire, save=save, timeout=timeout)

    def cards_get_verify_code(
        self, token: str, timeout: int = 10
    ) -> card_response.GetVerifyResponse:
        return self.cards.get_verify_code(token=token, timeout=timeout)

    def cards_verify(
        self, token: str, code: str, timeout: int = 10
    ) -> card_response.VerifyResponse:
        return self.cards.verify(token=token, code=code, timeout=timeout)

    def cards_remove(
        self, token: str, timeout: int = 10
    ) -> card_response.RemoveResponse:
        return self.cards.remove(token=token, timeout=timeout)

    def cards_check(
        self, token: str, timeout: int = 10
    ) -> card_response.CheckResponse:
        return self.cards.check(token=token, timeout=timeout)

    def cards_test(self) -> None:
        return self.cards.test()

    def receipts_create(
        self,
        account: dict,
        amount: t.Union[float, int],
        description: t.Optional[str] = None,
        detail: t.Optional[t.Dict] = None,
        timeout: int = 10,
    ) -> receipt_response.CreateResponse:
        return self.receipts.create(
            account=account, amount=amount, description=description,
            detail=detail, timeout=timeout
        )

    def receipts_pay(
        self, receipts_id: str, token: str, timeout: int = 10
    ) -> receipt_response.PayResponse:
        return self.receipts.pay(receipts_id=receipts_id, token=token, timeout=timeout)

    def receipts_send(
        self, receipts_id: str, phone: str, timeout: int = 10
    ) -> receipt_response.SendResponse:
        return self.receipts.send(receipts_id=receipts_id, phone=phone, timeout=timeout)

    def receipts_cancel(
        self, receipts_id: str, timeout: int = 10
    ) -> receipt_response.CancelResponse:
        return self.receipts.cancel(receipts_id=receipts_id, timeout=timeout)

    def receipts_check(
        self, receipts_id: str, timeout: int = 10
    ) -> receipt_response.CheckResponse:
        return self.receipts.check(receipts_id=receipts_id, timeout=timeout)

    def receipts_get(
        self, receipts_id: str, timeout: int = 10
    ) -> receipt_response.GetResponse:
        return self.receipts.get(receipts_id=receipts_id, timeout=timeout)

    def receipts_get_all(
        self, count: int, from_: int, to: int, offset: int, timeout: int = 10
    ) -> receipt_response.GetAllResponse:
        return self.receipts.get_all(
            count=count, from_=from_, to=to, offset=offset, timeout=timeout
        )

    def receipts_set_fiscal_data(
        self, receipt_id: str, qr_code_url: str, timeout: int = 10
    ) -> receipt_response.SetFiscalDataResponse:
        return self.receipts.set_fiscal_data(
            receipt_id=receipt_id, qr_code_url=qr_code_url, timeout=timeout
        )

    def receipts_test(self) -> None:
        if not hasattr(self, 'receipts'):
            raise AttributeError("Receipts not initialized. Provide payme_key in constructor.")
        return self.receipts.test()

    def generate_pay_link(self, id: int, amount: int, return_url: str) -> str:
        return self.initializer.generate_pay_link(id=id, amount=amount, return_url=return_url)

    def generate_fallback_link(self, form_fields: t.Optional[dict] = None) -> str:
        return self.initializer.generate_fallback_link(form_fields=form_fields)
