import base64
import binascii
import logging
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import views
from rest_framework.response import Response

from payme import exceptions
from payme.models import PaymeTransactions
from payme.types import response
from payme.util import time_to_payme, time_to_service

# 12 hours in ms — per Payme docs, transactions auto-cancel after this
TRANSACTION_TIMEOUT_MS = 43_200_000

logger = logging.getLogger(__name__)
AccountModel = import_string(settings.PAYME_ACCOUNT_MODEL)


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            message = "Invalid parameters received."
            logger.error(f"{message}: {exc}s {exc} {args} {kwargs}")
            raise exceptions.InternalServiceError(message) from exc

        except AccountModel.DoesNotExist as exc:
            logger.error(f"Account does not exist: {exc} {args} {kwargs}")
            raise exceptions.AccountDoesNotExist(str(exc)) from exc

        except ValidationError as exc:
            logger.error(f"Invalid account identifier {exc}")
            raise exceptions.AccountDoesNotExist("Invalid account identifier.")

        except PaymeTransactions.DoesNotExist as exc:
            logger.error(f"Transaction does not exist: {exc} {args} {kwargs}")
            raise exceptions.TransactionNotFound(str(exc)) from exc

        except exceptions.exception_whitelist as exc:
            raise exc
        except Exception as exc:
            logger.error(f"Unexpected error: {exc} {args} {kwargs}")
            raise exceptions.InternalServiceError(str(exc)) from exc

    return wrapper


class BasePaymeWebHookAPIView(views.APIView):
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        self.check_authorize(request)

        payme_methods = {
            "GetStatement": self.get_statement,
            "CancelTransaction": self.cancel_transaction,
            "PerformTransaction": self.perform_transaction,
            "CreateTransaction": self.create_transaction,
            "CheckTransaction": self.check_transaction,
            "CheckPerformTransaction": self.check_perform_transaction,
            "SetFiscalData": self.set_fiscal_data,
        }

        try:
            method = request.data["method"]
            params = request.data["params"]
        except KeyError as exc:
            message = f"Error processing webhook: {exc}"
            raise exceptions.InternalServiceError(message) from exc

        if method in payme_methods:
            result = payme_methods[method](params)
            return Response(result)

        raise exceptions.MethodNotFound("Method not supported yet!")

    @staticmethod
    def check_authorize(request):
        password = request.META.get('HTTP_AUTHORIZATION')
        if not password:
            raise exceptions.PermissionDenied("Missing authentication credentials")

        password = password.split()[-1]

        try:
            password = base64.b64decode(password).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise exceptions.PermissionDenied("Decoding error in authentication credentials") from exc

        try:
            payme_key = password.split(':')[-1]
        except IndexError as exc:
            raise exceptions.PermissionDenied("Invalid merchant key format") from exc

        if payme_key != settings.PAYME_KEY:
            raise exceptions.PermissionDenied("Invalid merchant key specified")

    @handle_exceptions
    def fetch_account(self, params: dict):
        account_value = params["account"].get(settings.PAYME_ACCOUNT_FIELD)
        if not account_value:
            raise exceptions.InvalidAccount("Missing account field in parameters.")

        account = AccountModel.objects.get(pk=account_value)
        return account

    @handle_exceptions
    def validate_amount(self, account, amount):
        if not settings.PAYME_ONE_TIME_PAYMENT:
            return True

        expected_amount = Decimal(getattr(account, settings.PAYME_AMOUNT_FIELD)) * 100
        received_amount = Decimal(amount)

        if expected_amount != received_amount:
            raise exceptions.IncorrectAmount(
                f"Invalid amount. Expected: {expected_amount}, received: {received_amount}"
            )

        return True

    @handle_exceptions
    def check_perform_transaction(self, params) -> response.CheckPerformTransaction:
        account = self.fetch_account(params)
        self.validate_amount(account, params.get('amount'))

        result = response.CheckPerformTransaction(allow=True)
        result_resp = result.as_resp()

        self.handle_pre_payment(params, result_resp)

        return result_resp

    @handle_exceptions
    def create_transaction(self, params) -> response.CreateTransaction:
        transaction_id = params["id"]
        amount = Decimal(params.get('amount', 0))
        account = self.fetch_account(params)

        self.validate_amount(account, amount)

        # Check if transaction with this ID already exists
        existing = PaymeTransactions.objects.filter(
            transaction_id=transaction_id
        ).first()

        if existing:
            # Check 12-hour timeout for INITIATING transactions
            if existing.is_created_in_payme():
                age_ms = time_to_payme(timezone.now()) - time_to_payme(existing.created_at)
                if age_ms > TRANSACTION_TIMEOUT_MS:
                    existing.mark_as_cancelled(
                        cancel_reason=4,
                        state=PaymeTransactions.CANCELED_DURING_INIT,
                    )
                    raise exceptions.UnableToPerformOperation(
                        "Transaction timed out (12h)."
                    )

            # Already exists and still valid — return it (idempotent)
            result = response.CreateTransaction(
                transaction=existing.transaction_id,
                state=existing.state,
                create_time=time_to_payme(existing.created_at),
            )
            return result.as_resp()

        # One-time payment: block if another active transaction exists for this account
        if settings.PAYME_ONE_TIME_PAYMENT:
            if (
                PaymeTransactions.objects.filter(account_id=account.pk)
                .exclude(transaction_id=transaction_id)
                .filter(state=PaymeTransactions.INITIATING)
                .exists()
            ):
                raise exceptions.TransactionAlreadyExists(
                    "Active transaction already exists for this account."
                )

        transaction = PaymeTransactions.objects.create(
            transaction_id=transaction_id,
            amount=amount,
            state=PaymeTransactions.INITIATING,
            account_id=account.pk,
        )

        result = response.CreateTransaction(
            transaction=transaction.transaction_id,
            state=transaction.state,
            create_time=time_to_payme(transaction.created_at),
        )
        result = result.as_resp()

        self.handle_created_payment(params, result)

        return result

    @handle_exceptions
    def perform_transaction(self, params) -> response.PerformTransaction:
        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

        # Already performed — return idempotent response
        if transaction.is_performed():
            result = response.PerformTransaction(
                transaction=transaction.transaction_id,
                state=transaction.state,
                perform_time=time_to_payme(transaction.performed_at),
            )
            return result.as_resp()

        # Cannot perform a cancelled transaction
        if transaction.is_cancelled():
            raise exceptions.UnableToPerformOperation(
                "Transaction is cancelled, cannot perform."
            )

        # Check 12-hour timeout for INITIATING transactions
        if transaction.is_created_in_payme():
            age_ms = time_to_payme(timezone.now()) - time_to_payme(transaction.created_at)
            if age_ms > TRANSACTION_TIMEOUT_MS:
                transaction.mark_as_cancelled(
                    cancel_reason=4,
                    state=PaymeTransactions.CANCELED_DURING_INIT,
                )
                raise exceptions.UnableToPerformOperation(
                    "Transaction timed out (12h), cannot perform."
                )

        transaction.mark_as_performed()

        result = response.PerformTransaction(
            transaction=transaction.transaction_id,
            state=transaction.state,
            perform_time=time_to_payme(transaction.performed_at),
        )
        result = result.as_resp()

        self.handle_successfully_payment(params, result)

        return result

    @handle_exceptions
    def check_transaction(self, params: dict) -> dict:
        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

        result = response.CheckTransaction(
            transaction=transaction.transaction_id,
            state=transaction.state,
            reason=transaction.cancel_reason,
            create_time=time_to_payme(transaction.created_at),
            perform_time=time_to_payme(transaction.performed_at),
            cancel_time=time_to_payme(transaction.cancelled_at),
        )

        return result.as_resp()

    @handle_exceptions
    def cancel_transaction(self, params) -> response.CancelTransaction:
        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

        if transaction.is_cancelled():
            return self._cancel_response(transaction)

        if transaction.is_performed():
            transaction.mark_as_cancelled(
                cancel_reason=params["reason"],
                state=PaymeTransactions.CANCELED
            )
        elif transaction.is_created_in_payme():
            transaction.mark_as_cancelled(
                cancel_reason=params["reason"],
                state=PaymeTransactions.CANCELED_DURING_INIT
            )

        result = self._cancel_response(transaction)

        self.handle_cancelled_payment(params, result)

        return result

    @handle_exceptions
    def get_statement(self, params) -> response.GetStatement:
        date_range = [time_to_service(params['from']), time_to_service(params['to'])]

        transactions = PaymeTransactions.objects.filter(
            created_at__range=date_range
        ).order_by('created_at')

        result = response.GetStatement(transactions=[])

        for transaction in transactions:
            result.transactions.append({
                "id": transaction.transaction_id,
                "time": time_to_payme(transaction.created_at),
                "amount": transaction.amount,
                "account": {
                    settings.PAYME_ACCOUNT_FIELD: transaction.account_id
                },
                "create_time": time_to_payme(transaction.created_at),
                "perform_time": time_to_payme(transaction.performed_at),
                "cancel_time": time_to_payme(transaction.cancelled_at),
                "transaction": transaction.transaction_id,
                "state": transaction.state,
                "reason": transaction.cancel_reason,
                "receivers": None,
            })

        return result.as_resp()

    @handle_exceptions
    def set_fiscal_data(self, params):
        """
        Stores PERFORM and CANCEL fiscal data separately per Payme docs.
        """
        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

        fiscal_data = params.get("fiscal_data")
        if not fiscal_data:
            raise exceptions.InvalidFiscalParams(
                "Missing fiscal_data field in parameters."
            )

        fiscal_type = params.get("type")

        if fiscal_type not in ("PERFORM", "CANCEL"):
            raise exceptions.InvalidFiscalParams(
                f"Invalid fiscal type. Expected 'PERFORM' or 'CANCEL', got: {fiscal_type}"
            )

        # Store PERFORM and CANCEL data separately — never overwrite the other
        existing = transaction.fiscal_data or {}
        if fiscal_type == "PERFORM":
            existing["perform_data"] = fiscal_data
        else:
            existing["cancel_data"] = fiscal_data
        transaction.fiscal_data = existing
        transaction.save()

        result = response.SetFiscalData(success=True)
        return result.as_resp()

    def _cancel_response(self, transaction):
        result = response.CancelTransaction(
            transaction=transaction.transaction_id,
            state=transaction.state,
            cancel_time=time_to_payme(transaction.cancelled_at),
        )
        return result.as_resp()

    def handle_pre_payment(self, params, result, *args, **kwargs):
        pass

    def handle_created_payment(self, params, result, *args, **kwargs):
        pass

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        pass

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        pass
