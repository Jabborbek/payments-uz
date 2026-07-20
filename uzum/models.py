from django.db import models
from django.utils import timezone


class UzumTransactions(models.Model):
    PENDING = 0
    PAID = 1
    CANCELED = -1

    STATE = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (CANCELED, "Canceled"),
    ]

    trans_id = models.CharField(max_length=255, unique=True, db_index=True)
    order_id = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    state = models.IntegerField(choices=STATE, default=PENDING)
    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Uzum Transaction"
        verbose_name_plural = "Uzum Transactions"
        ordering = ["-created_at"]
        db_table = "uzum_transactions"

    def __str__(self):
        return f"Uzum #{self.trans_id} Order: {self.order_id} - {self.get_state_display()}"

    @classmethod
    def get_by_trans_id(cls, trans_id: str):
        return cls.objects.get(trans_id=trans_id)

    def is_paid(self) -> bool:
        return self.state == self.PAID

    def is_cancelled(self) -> bool:
        return self.state == self.CANCELED

    def is_pending(self) -> bool:
        return self.state == self.PENDING

    def mark_as_paid(self) -> bool:
        if self.state != self.PENDING:
            return False
        self.state = self.PAID
        self.performed_at = timezone.now()
        self.save()
        return True

    def mark_as_cancelled(self, reason: str = None) -> "UzumTransactions":
        if self.state == self.CANCELED:
            return self
        self.state = self.CANCELED
        self.cancel_reason = reason
        self.cancelled_at = timezone.now()
        self.save()
        return self
