import base64
import binascii
import logging
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import views
from rest_framework.response import Response

from uzum.exceptions.merchant import UzumError
from uzum.models import UzumTransactions
from uzum.util import time_to_uzum

logger = logging.getLogger(__name__)
AccountModel = import_string(settings.UZUM_ACCOUNT_MODEL)

# Uzum IP whitelist — faqat shu IP'lardan kelgan so'rovlar qabul qilinadi
UZUM_ALLOWED_IPS = getattr(settings, 'UZUM_ALLOWED_IPS', None)


class BaseUzumWebHookAPIView(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    # ─── Security: IP whitelist + Basic Auth ───────────────────────

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._check_ip(request)
        self._check_auth(request)

    def _check_ip(self, request):
        """Uzum IP whitelist tekshiruvi."""
        if not UZUM_ALLOWED_IPS:
            return

        ip = self._get_client_ip(request)
        if ip not in UZUM_ALLOWED_IPS:
            logger.warning(f"Uzum webhook blocked from IP: {ip}")
            raise views.exceptions.PermissionDenied(
                f"IP {ip} is not in the allowed list."
            )

    @staticmethod
    def _get_client_ip(request) -> str:
        """Proxy orqasidagi haqiqiy IP ni olish."""
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    @staticmethod
    def _check_auth(request):
        """HTTP Basic Auth tekshiruvi."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            raise views.exceptions.AuthenticationFailed("Missing Authorization header.")

        try:
            scheme, credentials = auth_header.split(' ', 1)
            if scheme.lower() != 'basic':
                raise views.exceptions.AuthenticationFailed("Invalid auth scheme.")

            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
        except (ValueError, binascii.Error, UnicodeDecodeError):
            raise views.exceptions.AuthenticationFailed("Malformed Authorization header.")

        if username != settings.UZUM_USERNAME or password != settings.UZUM_PASSWORD:
            raise views.exceptions.AuthenticationFailed("Invalid credentials.")

    # ─── Routing ───────────────────────────────────────────────────

    def post(self, request, *args, **kwargs):
        action = kwargs.get('action', '')

        handlers = {
            'check': self._handle_check,
            'create': self._handle_create,
            'confirm': self._handle_confirm,
            'reverse': self._handle_reverse,
            'status': self._handle_status,
        }

        handler = handlers.get(action)
        if not handler:
            return self._error_response(
                request.data, UzumError.UNKNOWN_OPERATION
            )

        try:
            return handler(request.data)
        except Exception as exc:
            logger.error(f"Uzum webhook error [{action}]: {exc}", exc_info=True)
            return self._error_response(
                request.data, UzumError.VALIDATION_ERROR
            )

    # ─── Validators ────────────────────────────────────────────────

    def _validate_service_id(self, data: dict) -> bool:
        service_id = data.get('serviceId')
        if service_id != settings.UZUM_SERVICE_ID:
            return False
        return True

    def _fetch_account(self, params: dict):
        account_field = settings.UZUM_ACCOUNT_FIELD
        account_value = params.get(account_field)
        if not account_value:
            return None
        try:
            return AccountModel.objects.get(pk=account_value)
        except (AccountModel.DoesNotExist, ValueError):
            return None

    def _validate_amount(self, account, amount_tiyin: int) -> bool:
        if not getattr(settings, 'UZUM_ONE_TIME_PAYMENT', False):
            return True
        expected = Decimal(getattr(account, settings.UZUM_AMOUNT_FIELD)) * 100
        return expected == Decimal(amount_tiyin)

    # ─── CHECK ─────────────────────────────────────────────────────

    def _handle_check(self, data: dict) -> Response:
        if not self._validate_service_id(data):
            return self._error_response(data, UzumError.INVALID_SERVICE_ID)

        params = data.get('params', {})
        account = self._fetch_account(params)
        if not account:
            return self._error_response(data, UzumError.ORDER_NOT_FOUND)

        result = {
            "serviceId": data.get('serviceId'),
            "timestamp": data.get('timestamp'),
            "status": "OK",
            "data": {
                "account": {
                    "value": str(account.pk),
                }
            }
        }

        self.handle_check(params, result)

        return Response(result)

    # ─── CREATE ────────────────────────────────────────────────────

    def _handle_create(self, data: dict) -> Response:
        if not self._validate_service_id(data):
            return self._error_response(data, UzumError.INVALID_SERVICE_ID)

        trans_id = data.get('transId')
        amount = data.get('amount', 0)
        params = data.get('params', {})

        if not trans_id:
            return self._error_response(data, UzumError.NOT_ENOUGH_PARAMS)

        # Dublikat tekshiruvi
        existing = UzumTransactions.objects.filter(trans_id=trans_id).first()
        if existing:
            if existing.is_paid():
                return self._error_response(data, UzumError.ALREADY_PROCESSED)
            if existing.is_cancelled():
                return self._error_response(data, UzumError.PAYMENT_CANCELLED)
            # PENDING — idempotent javob
            return self._create_response(existing, data)

        account = self._fetch_account(params)
        if not account:
            return self._error_response(data, UzumError.ORDER_NOT_FOUND)

        if not self._validate_amount(account, amount):
            return self._error_response(data, UzumError.VALIDATION_ERROR)

        transaction = UzumTransactions.objects.create(
            trans_id=trans_id,
            order_id=str(account.pk),
            amount=Decimal(amount),
            state=UzumTransactions.PENDING,
        )

        result = self._create_response(transaction, data)

        self.handle_created_payment(params, result)

        return result

    def _create_response(self, transaction, data: dict) -> Response:
        result = {
            "serviceId": data.get('serviceId'),
            "timestamp": data.get('timestamp'),
            "status": "CREATED",
            "transTime": time_to_uzum(transaction.created_at),
            "transId": transaction.trans_id,
            "amount": int(transaction.amount),
        }
        return Response(result)

    # ─── CONFIRM ───────────────────────────────────────────────────

    def _handle_confirm(self, data: dict) -> Response:
        if not self._validate_service_id(data):
            return self._error_response(data, UzumError.INVALID_SERVICE_ID)

        trans_id = data.get('transId')
        if not trans_id:
            return self._error_response(data, UzumError.NOT_ENOUGH_PARAMS)

        try:
            transaction = UzumTransactions.get_by_trans_id(trans_id)
        except UzumTransactions.DoesNotExist:
            return self._error_response(data, UzumError.ORDER_NOT_FOUND)

        if transaction.is_paid():
            return self._confirm_response(transaction, data)

        if transaction.is_cancelled():
            return self._error_response(data, UzumError.PAYMENT_CANCELLED)

        if not transaction.is_pending():
            return self._error_response(data, UzumError.ALREADY_PROCESSED)

        transaction.mark_as_paid()

        result = self._confirm_response(transaction, data)

        self.handle_successfully_payment(data, result)

        return result

    def _confirm_response(self, transaction, data: dict) -> Response:
        result = {
            "serviceId": data.get('serviceId'),
            "transId": transaction.trans_id,
            "status": "CONFIRMED",
            "confirmTime": time_to_uzum(transaction.performed_at),
        }
        return Response(result)

    # ─── REVERSE ───────────────────────────────────────────────────

    def _handle_reverse(self, data: dict) -> Response:
        if not self._validate_service_id(data):
            return self._error_response(data, UzumError.INVALID_SERVICE_ID)

        trans_id = data.get('transId')
        if not trans_id:
            return self._error_response(data, UzumError.NOT_ENOUGH_PARAMS)

        try:
            transaction = UzumTransactions.get_by_trans_id(trans_id)
        except UzumTransactions.DoesNotExist:
            return self._error_response(data, UzumError.ORDER_NOT_FOUND)

        if transaction.is_cancelled():
            return self._reverse_response(transaction, data)

        transaction.mark_as_cancelled(reason="reversed_by_uzum")

        result = self._reverse_response(transaction, data)

        self.handle_cancelled_payment(data, result)

        return result

    def _reverse_response(self, transaction, data: dict) -> Response:
        result = {
            "serviceId": data.get('serviceId'),
            "transId": transaction.trans_id,
            "status": "REVERSED",
            "reverseTime": time_to_uzum(transaction.cancelled_at),
            "amount": int(transaction.amount),
        }
        return Response(result)

    # ─── STATUS ────────────────────────────────────────────────────

    def _handle_status(self, data: dict) -> Response:
        if not self._validate_service_id(data):
            return self._error_response(data, UzumError.INVALID_SERVICE_ID)

        trans_id = data.get('transId')
        if not trans_id:
            return self._error_response(data, UzumError.NOT_ENOUGH_PARAMS)

        try:
            transaction = UzumTransactions.get_by_trans_id(trans_id)
        except UzumTransactions.DoesNotExist:
            return self._error_response(data, UzumError.ORDER_NOT_FOUND)

        state_map = {
            UzumTransactions.PENDING: "CREATED",
            UzumTransactions.PAID: "CONFIRMED",
            UzumTransactions.CANCELED: "REVERSED",
        }

        result = {
            "serviceId": data.get('serviceId'),
            "transId": transaction.trans_id,
            "status": state_map.get(transaction.state, "CREATED"),
        }
        return Response(result)

    # ─── Error response ────────────────────────────────────────────

    def _error_response(self, data: dict, error_code: int) -> Response:
        result = {
            "serviceId": data.get('serviceId'),
            "timestamp": data.get('timestamp'),
            "status": "FAILED",
            "errorCode": error_code,
        }
        logger.warning(f"Uzum error response: {error_code} — {UzumError.get_message(error_code)}")
        return Response(result)

    # ─── Callback hooks (override in subclass) ─────────────────────

    def handle_check(self, params, result, *args, **kwargs):
        pass

    def handle_created_payment(self, params, result, *args, **kwargs):
        pass

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        pass

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        pass
