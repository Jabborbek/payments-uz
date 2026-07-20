import logging
import typing as t

import requests

logger = logging.getLogger(__name__)


class UzumHttpClient:
    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url.rstrip('/')
        self.headers = headers

    def post(self, path: str, json: dict, timeout: int = 15) -> dict:
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(
                url=url,
                headers=self.headers,
                json=json,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            error_code = data.get('errorCode', 0)
            if error_code != 0:
                raise UzumAPIError(
                    code=error_code,
                    message=data.get('message', 'Unknown error'),
                )

            return data

        except requests.exceptions.RequestException as exc:
            logger.error(f"Uzum API request failed: {exc}")
            raise UzumNetworkError(str(exc)) from exc


class UzumAPIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Uzum API error {code}: {message}")


class UzumNetworkError(Exception):
    pass
