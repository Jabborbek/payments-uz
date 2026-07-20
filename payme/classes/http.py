import requests

from payme.exceptions import general as exc


networking_errors = (
    requests.exceptions.Timeout,
    requests.exceptions.HTTPError,
    requests.exceptions.ConnectionError,
    requests.exceptions.TooManyRedirects,
    requests.exceptions.URLRequired,
    requests.exceptions.MissingSchema,
    requests.exceptions.InvalidURL,
    requests.exceptions.InvalidHeader,
    requests.exceptions.JSONDecodeError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
    requests.exceptions.SSLError,
    requests.exceptions.ProxyError,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.StreamConsumedError,
    requests.exceptions.RequestException
)


class HttpClient:
    def __init__(self, url: str, headers: dict = None):
        self.url = url
        self.headers = headers

    def post(self, json: dict, timeout: int = 10):
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                json=json,
                timeout=timeout
            )
            response.raise_for_status()
            response_data = response.json()

            if "error" in response_data:
                return self.handle_payme_error(response_data["error"])

            return response_data

        except networking_errors as exc_data:
            raise exc.PaymeNetworkError(data=exc_data)

    def handle_payme_error(self, error: dict):
        error_code = error.get("code", "Unknown code")
        error_message = error.get("message", "Unknown error")
        error_data = error.get("data", "")

        exception_class = exc.errors_map.get(error_code, exc.BaseError)
        exception_class.message = error_message

        if exception_class == exc.BaseError:
            raise exc.BaseError(code=error_code, message=error_message)

        raise exception_class(data=error_data)
