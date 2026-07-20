from django.db import models
from django.utils import timezone


class PaymeTransactions(models.Model):
    CREATED = 0
    INITIATING = 1
    SUCCESSFULLY = 2
    CANCELED = -2
    CANCELED_DURING_INIT = -1

    STATE = [
        (CREATED, "Created"),
        (INITIATING, "Initiating"),
        (SUCCESSFULLY, "Successfully"),
        (CANCELED, "Canceled after successful performed"),
        (CANCELED_DURING_INIT, "Canceled during initiation"),
    ]

    transaction_id = models.CharField(max_length=50)
    account_id = models.CharField(max_length=256, null=False)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    state = models.IntegerField(choices=STATE, default=CREATED)
    fiscal_data = models.JSONField(default=dict)
    cancel_reason = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    performed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    cancelled_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Payme Transaction"
        verbose_name_plural = "Payme Transactions"
        ordering = ["-created_at"]
        db_table = "payme_transactions"

    def __str__(self):
        return f"Payme Transaction #{self.transaction_id} Account: {self.account_id} - {self.state}"

    @classmethod
    def get_by_transaction_id(cls, transaction_id):
        return cls.objects.get(transaction_id=transaction_id)

    def is_performed(self) -> bool:
        return self.state == self.SUCCESSFULLY

    def is_cancelled(self) -> bool:
        return self.state in [self.CANCELED, self.CANCELED_DURING_INIT]

    def is_created(self) -> bool:
        return self.state == self.CREATED

    def is_created_in_payme(self) -> bool:
        return self.state == self.INITIATING

    def mark_as_cancelled(self, cancel_reason: int, state: int) -> "PaymeTransactions":
        if self.state == state:
            return self
        self.state = state
        self.cancel_reason = cancel_reason
        self.cancelled_at = timezone.now()
        self.save()
        return self

    def mark_as_performed(self) -> bool:
        if self.state != self.INITIATING:
            return False
        self.state = self.SUCCESSFULLY
        self.performed_at = timezone.now()
        self.save()
        return True
