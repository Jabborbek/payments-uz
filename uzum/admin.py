from django.conf import settings
from django.contrib import admin

from uzum.models import UzumTransactions


class UzumTransactionsUI(admin.ModelAdmin):
    list_display = ('pk', 'trans_id', 'order_id', 'amount', 'state', 'created_at')
    list_filter = ('state', 'created_at')
    search_fields = ('trans_id', 'order_id')
    ordering = ('-created_at',)


if not getattr(settings, 'UZUM_DISABLE_ADMIN', False):
    admin.site.register(UzumTransactions, UzumTransactionsUI)
