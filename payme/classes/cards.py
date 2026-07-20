from typing import Optional

from payme.classes.http import HttpClient
from payme.types.response import cards as response


ALLOWED_METHODS = {
    "cards.create": response.CardsCreateResponse,
    "cards.get_verify_code": response.GetVerifyResponse,
    "cards.verify": response.VerifyResponse,
    "cards.remove": response.RemoveResponse,
    "cards.check": response.CheckResponse
}


class Cards:
    def __init__(self, url: str, payme_id: str) -> None:
        headers = {
            "X-Auth": payme_id,
            "Content-Type": "application/json"
        }
        self.http = HttpClient(url, headers)

    def create(self, number: str, expire: str, save: bool = False,
               timeout: int = 10) -> response.CardsCreateResponse:
        method = "cards.create"
        params = {"card": {"number": number, "expire": expire}, "save": save}
        return self._post_request(method, params, timeout)

    def get_verify_code(self, token: str, timeout: int = 10) -> response.GetVerifyResponse:
        method = "cards.get_verify_code"
        params = {"token": token}
        return self._post_request(method, params, timeout)

    def verify(self, token: str, code: str, timeout: int = 10) -> response.VerifyResponse:
        method = "cards.verify"
        params = {"token": token, "code": code}
        return self._post_request(method, params, timeout)

    def remove(self, token: str, timeout: int = 10) -> response.RemoveResponse:
        method = "cards.remove"
        params = {"token": token}
        return self._post_request(method, params, timeout)

    def check(self, token: str, timeout: int = 10) -> response.CheckResponse:
        method = "cards.check"
        params = {"token": token}
        return self._post_request(method, params, timeout)

    def _post_request(self, method: str, params: dict,
                      timeout: int = 10) -> response.Common:
        json = {"method": method, "params": params}
        dict_result = self.http.post(json, timeout)
        response_class = ALLOWED_METHODS[method]
        return response_class.from_dict(dict_result)

    def test(self):
        number = "8600495473316478"
        expire = "0399"
        expected_number = "860049******6478"
        expected_expire = "03/99"
        verify_code = "666666"

        create_response = self.create(number=number, expire=expire)
        token = create_response.result.card.token

        self._assert_and_print(
            create_response.result.card.number == expected_number,
            "Card number matched.",
            test_case="Card Creation - Number Validation"
        )
        self._assert_and_print(
            create_response.result.card.expire == expected_expire,
            "Expiration date matched.",
            test_case="Card Creation - Expiration Date Validation"
        )

        get_verify_response = self.get_verify_code(token=token)
        self._assert_and_print(
            get_verify_response.result.sent is True,
            "Verification code requested successfully.",
            test_case="Verification Code Request"
        )

        verify_response = self.verify(token=token, code=verify_code)
        self._assert_and_print(
            verify_response.result.card.verify is True,
            "Verification code validated successfully.",
            test_case="Code Verification"
        )

        check_response = self.check(token=token)
        self._assert_and_print(
            check_response.result.card.verify is True,
            "Card status verified successfully.",
            test_case="Card Status Check"
        )

        remove_response = self.remove(token=token)
        self._assert_and_print(
            remove_response.result.success is True,
            "Card removed successfully.",
            test_case="Card Removal"
        )

    def _assert_and_print(self, condition: bool, success_message: str,
                          test_case: Optional[str] = None):
        try:
            assert condition, "Assertion failed!"
            print(f"Success: {success_message}")
        except AssertionError as exc:
            error_message = (
                f"Test Case Failed: {test_case or 'Unknown Test Case'}\n"
                f"Error Details: {str(exc)}"
            )
            print(error_message)
            raise AssertionError(error_message) from exc
